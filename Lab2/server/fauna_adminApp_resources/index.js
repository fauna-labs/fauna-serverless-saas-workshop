// Copyright Fauna, Inc.
// SPDX-License-Identifier: MIT-0

import { Client, fql } from "fauna";

const args = process.argv.slice(2);
const FAUNA_API_KEY = args[0];


const client = new Client({
  secret: FAUNA_API_KEY,
});

try {
  const q = fql`
  let tenantColl = Collection.byName('tenant')
  if (tenantColl == null) {
    Collection.create({
      name: 'tenant',
      indexes: {
        byName: {
          terms: [{ field: "tenantName" }]
        }
      }      
    })
  }
  let tenantUserColl = Collection.byName('tenantUser')
  if (tenantUserColl == null) {
    Collection.create({
      name: 'tenantUser',
      indexes: {
        usernamesByTenantId: {
          terms: [{ field: "tenant_id" }],
          values: [{ field: "user_name" }]
        }
      }
    })
  }  
  `;

  const res = await client.query(q);
  console.log(JSON.stringify(res, null, 2));

} catch (err) {
  console.log(err);
}
