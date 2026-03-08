#! /bin/bash

INKSCAPE="/usr/bin/inkscape"
OPTIPNG="/usr/bin/optipng"
OUTPUT_EXT=".png"

LINK_NAMES=("bottom-inactive"
            "bottom-left-inactive"
            "bottom-right-active"
            "left-active"
            "left-inactive"
            "menu-inactive"
            "menu-prelight"
            "menu-pressed"
            "right-inactive")

LINK_TARGETS=("bottom-active"
            "bottom-left-active"
            "bottom-right-inactive"
            "right-active"
            "right-active"
            "menu-active"
            "menu-active"
            "menu-active"
            "right-active")


THEME_NAME="Synthesis-Dark"

rendered_asset_path() {
    printf '%s/%s%s' "$1" "$2" "$OUTPUT_EXT"
}

for  screen in '' '-hdpi' '-xhdpi'; do

    case "${screen}" in
    -hdpi)
        DPI='144'
        ;;
    -xhdpi)
        DPI='192'
        ;;
    *)
        DPI='96'
        ;;
    esac

    ASSETS_DIR="${THEME_NAME}${screen}/xfwm4"
    mkdir -p "${ASSETS_DIR}"

    for i in assets/*; do
        BASE_FILE_NAME=$(basename -s .svg "${i}")
        OUTPUT_PATH=$(rendered_asset_path "${ASSETS_DIR}" "${BASE_FILE_NAME}")

        if [ -f "${OUTPUT_PATH}" ]; then
            echo "${OUTPUT_PATH} exists."
        else
            echo
            echo "Rendering ${OUTPUT_PATH}"
            "${INKSCAPE}" --export-dpi="${DPI}" \
                    --export-filename="${OUTPUT_PATH}" "${i}" \
            && "${OPTIPNG}" -o7 --quiet "${OUTPUT_PATH}"
        fi
    done

    for i in "${!LINK_NAMES[@]}"; do
        ln -sf "${LINK_TARGETS[$i]}${OUTPUT_EXT}" "$(rendered_asset_path "${ASSETS_DIR}" "${LINK_NAMES[$i]}")"
    done
    cp themerc "${ASSETS_DIR}/"
done
exit 0
