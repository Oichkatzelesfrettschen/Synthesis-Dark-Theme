set -l files 'checkbox' 'radio'
set -l states 'unchecked' 'checked' 'mixed'
set -l sub_states 'active' 'hover' 'insensitive'
set -l output_ext '.png'

for f in $files;
	for s in $states;
		ln -sf ../../assets/$f-$s$output_ext ./assets/$f-$s$output_ext
		for i in $sub_states;
			ln -sf ../../assets/$f-$s-$i$output_ext ./assets/$f-$s-$i$output_ext
		;end
	;end

;end
