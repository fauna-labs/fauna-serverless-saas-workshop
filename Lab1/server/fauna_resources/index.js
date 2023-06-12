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
  let orderColl = Collection.byName('order')
  if (orderColl == null) {
    Collection.create({ name: 'order' })
  }
  let productColl = Collection.byName('product')
  if (productColl == null) {
    Collection.create({ name: 'product' })
  }  
  `;

  const res = await client.query(q);
  console.log(JSON.stringify(res, null, 2));

} catch (err) {
  console.log(err);
}
