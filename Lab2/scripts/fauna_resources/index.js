const exec = require('child_process').exec;

const args = process.argv.slice(2);
const FAUNA_API_KEY = args[0];

function execute(command, callback){
    exec(command, function(error, stdout, stderr){ callback(stdout); });
};

execute(`node_modules/.bin/fauna-schema-migrate -k ${FAUNA_API_KEY} apply`, (y)=> {
  console.log(y)
})

