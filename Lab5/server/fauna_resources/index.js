require('dotenv').config();
const exec = require('child_process').exec;
const faunadb = require('faunadb');

const client = new faunadb.Client({
  secret: process.env.FAUNADB_SECRET,
  domain: process.env.FAUNADB_DOMAIN
});

const q = faunadb.query;
const { Map, Paginate, Documents, Collection, 
  Match, Index, 
  Lambda, Let, Get, Var, Select,
  Concat, Exists, Database 
} = q;

function execute(command, callback){
    exec(command, function(error, stdout, stderr){ callback(stdout); });
};

client.query( 
  Map(
    Paginate(Documents(Collection("tenant"))),
    Lambda(
      "x",
      Let(
        {
          tenant: Get(Var("x")),
          id: Select(["ref", "id"], Var("tenant")),
          name: Concat(["tenant_", Var("id")], ""),
          exists: Exists(Database(Var("name")))
        },
        {
          exists: Var("exists"),
          id: Var("id"),
          name: Var("name")
        }
      )
    )
  )  
).then(res=>{
  console.log(res);
  const data = res.data;
  data.map(res => {
    if (res.exists) {
      execute(`node_modules/.bin/fauna-schema-migrate -k $FAUNADB_SECRET:tenant_${res.id}:server apply`, (y)=> {
        console.log(y)
      })
    }
  })
})


