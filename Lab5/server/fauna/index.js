// ES6
// import 'dotenv/config';
// import faunadb from 'faunadb';
// import cp from 'child_process';
// const exec = cp.exec;

require('dotenv').config();
const exec = require('child_process').exec;
const faunadb = require('faunadb');

const client = new faunadb.Client({
  secret: process.env.FAUNADB_SECRET,
  domain: process.env.FAUNADB_DOMAIN
});

const q = faunadb.query;
const { Map, Paginate, Collections, Documents, Collection, Match, Index, Lambda, Select, Get, Var } = q;

function execute(command, callback){
    exec(command, function(error, stdout, stderr){ callback(stdout); });
};

client.query( 
  Map(
    Paginate(Collections()),
    Lambda("x", Get(Var("x")))
  )
).then(res=>{
  console.log(res);
})

// const data = res.data;
// data.map(x => {
//   execute('echo $FAUNADB_SECRET', (y)=> {
//     console.log(`${x.ref} - ${y}`)
//   })
// })

execute('node_modules/.bin/fauna-schema-migrate -k $FAUNADB_SECRET -c fsm4 apply', (y)=> {
  console.log(y)
})
