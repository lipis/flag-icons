<?php

function trueBlack($files, $directory)
{
	foreach($files as $file)
	{
		$filepath = $directory .'/'. $file;

		$svg = file_get_contents($filepath);

		$svg = str_replace('fill="#000001"', 'fill="#000"', $svg);

		file_put_contents($filepath, $svg);

		echo 'Done: '. $filepath .'<br>';
	}
}

$directory = 'flags/1x1';
$files = array_diff(scandir($directory), ['..', '.']);

trueBlack($files, $directory);

$directory = 'flags/4x3';
$files = array_diff(scandir($directory), ['..', '.']);

trueBlack($files, $directory);
