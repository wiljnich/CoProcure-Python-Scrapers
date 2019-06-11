var fs = require('fs');

let count = 0;
let totalFiles = 0;
let filesProcessed = 0;
let fileSet = 1;

function readFiles(dirname, onFileContent, onError) {
  fs.readdir(dirname, function(err, filenames) {
    if (err) {
      onError(err);
      return;
    }
    filenames.forEach(function(filename) {
      if(filename.indexOf('.json') > -1) {
        totalFiles++;
        fs.readFile(dirname + filename, 'utf-8', function(err, content) {
          if (err) {
            onError(err);
            return;
          }
          onFileContent(filename, content);
        });
      }
    });
  });
}


readFiles('./output-cloudsearch/',function(filename, content) {
  let fileContent = JSON.parse(content);
  fileContent.fields.amendments_files = fileContent.fields.amendment_files;
  delete fileContent.fields.amendment_files;

  fs.writeFile('./output-cloudsearch/'+filename, JSON.stringify(fileContent), 'utf8', function() {
    console.log('wrote file ')
  });
  
}, function(err) {
  console.log(err)
})