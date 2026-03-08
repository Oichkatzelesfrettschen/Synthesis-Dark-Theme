set -l  wm 'close' 'close_prelight' 'close_unfocused' 'min' 'min_prelight' 'maximize' 'maximize_prelight'
set -l path '../../assets/'
set -l output_ext '.png'
for item in $wm
	set -l output_path $path$item'@2'$output_ext
	inkscape $path$item.svg -o $output_path --export-dpi=192; optipng -o7 --quiet $output_path
end
