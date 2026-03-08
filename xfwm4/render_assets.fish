set -l red (set_color -o red)
set -l cyan (set_color -o cyan)
set -l output_ext '.png'

for i in assets/*;
	set -l file_name (basename $i .svg)
	set -l output_path ./$file_name$output_ext
	if test -f $output_path
		echo $red$file_name exists
	else
		echo $cyan'Creating '$output_path
		convert -background none $i $output_path
	end
;end
