require('dotenv').config();
const exec = require('child_process').exec;
const faunadb = require('faunadb');

const args = process.argv.slice(2);
const FAUNA_API_KEY = args[0];

const client = new faunadb.Client({
  secret: FAUNA_API_KEY
});

const q = faunadb.query;
const { Map, Paginate, Documents, Collection, 
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
      execute(`node_modules/.bin/fauna-schema-migrate -k ${FAUNA_API_KEY}:tenant_${res.id}:server apply`, (y)=> {
        console.log(y)
      })
    }
  })
})


