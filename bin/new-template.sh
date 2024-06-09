#! /bin/zsh

echo "|=====================|"
echo "| New Prompt Template |"
echo "|=====================|"

echo $1

# Set CWD To Script Directory
cd "$(dirname $1)"

# Get Filename
read "? Enter File Name ? " FILENAME

# Calculate Date as YYYYMMDDHHDDSS
echo "> Calculating Date"
DATE=$(date +%Y%m%d%H%M%S)

# Copy Template
cp ../var/prompts/Template.md ../var/prompts/$DATE-$FILENAME.md
echo "> Created: $DATE-$FILENAME.md"