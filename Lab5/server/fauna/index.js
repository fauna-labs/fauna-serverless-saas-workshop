import 'dotenv/config';
import faunadb from 'faunadb';
import cp from 'child_process';

const client = new faunadb.Client({
  secret: process.env.FAUNADB_SECRET,
  domain: process.env.FAUNADB_DOMAIN
});

const q = faunadb.query;
const { Map, Paginate, Documents, Collection, Match, Index, Lambda, Select, Get, Var } = q;

const exec = cp.exec;
function execute(command, callback){
    exec(command, function(error, stdout, stderr){ callback(stdout); });
};

const res = await client.query( 
  Map(
    Paginate(Documents(Collection("Users"))),
    Lambda("x", Get(Var("x")))
  )
)
// console.log(res);

// const data = res.data;
// data.map(x => {
//   execute('echo $FAUNADB_SECRET', (y)=> {
//     console.log(`${x.ref} - ${y}`)
//   })
// })

execute('echo $FAUNADB_SECRET', (y)=> {
  console.log(`FAUNADB_SECRET: ${y}`)
})
