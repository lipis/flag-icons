#Creates the proper lib.zip file from the lib folder
cd lib
rm ../lib.zip
zip -r ../lib.zip *
cd ..
