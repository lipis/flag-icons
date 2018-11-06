#!/bin/bash

usage() {
  echo "$1"
  echo "Usage: $0 <input_folder> <output_folder>"
  echo "Quit..."
}

INPUT_FOLDER=$1
OUTPUT_FOLDER=$2

if [ -z "$INPUT_FOLDER" ]; then usage "Input Folder missing!"; exit 1; fi
if [ -z "$OUTPUT_FOLDER" ]; then usage "Output Folder missing!"; exit 1; fi

command -v rsvg-convert >/dev/null 2>&1 || { 
  echo >&2 usage "RsvgConvert missing - Install using \"brew install librsvg\"."; exit 1;
}

SVG_LIST=($(ls $INPUT_FOLDER/*.svg))
JSON="{\"images\":[{\"idiom\":\"universal\",\"filename\":\"##FILE_NAME##\"}],\"info\":{\"version\":1,\"author\":\"xcode\"},\"properties\":{\"preserves-vector-representation\":true}}"
ASSET_FOLDER="/tmp/Assets.xcassets"


rm -rf $ASSET_FOLDER

for SVG in "${SVG_LIST[@]}"; do
  ID=$(echo $(basename $SVG) | cut -d. -f1)
  IMAGESET="$ASSET_FOLDER/$ID.imageset"

  mkdir -p $IMAGESET
  rsvg-convert -f pdf -o $IMAGESET/$ID.pdf $SVG
  echo ${JSON/"##FILE_NAME##"/"$ID.pdf"} > "$IMAGESET/Contents.json"
done

mv $ASSET_FOLDER $OUTPUT_FOLDER
