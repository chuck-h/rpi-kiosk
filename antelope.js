// wharfkit experiments
require('dotenv').config()

const { ContractKit } = require("@wharfkit/contract")
const { APIClient } = require("@wharfkit/antelope")
const { Session } = require("@wharfkit/session")
const { WalletPluginPrivateKey } = require("@wharfkit/wallet-plugin-privatekey")

const { NATS_URL } = process.env
const { connect } = require("nats")
const servers = NATS_URL || "nats://localhost:4222";


console.log("after imports  0.00")
var startTime = performance.now()

const contractKit = new ContractKit({
  client: new APIClient({
    url: "https://telos.caleos.io",
  }),
})

const chain = {
  id: "4667b205c6838ef70ff7988f6e8257e8be0e1284a2f59699054a018f743b1d11",
  url: "https://telos.caleos.io",
}

const accountName = "nottoosecure"
const permissionName = "active"

const privateKey = "5KcQMuby4wUCA9Mo5xU1rrXegtdPskmQzbdqhJ8BDfMRP97z3Ed"
const walletPlugin = new WalletPluginPrivateKey(privateKey)

const session = new Session({
  actor: accountName,
  permission: permissionName,
  chain,
  walletPlugin,
})

console.log(`creating action ${(performance.now()-startTime)/1000}`)
const badgeAction = {
  account: "microbadger2",
  name: "init",
  authorization: [session.permissionLevel],
  data: {
    badge: "kiosk0",
    badgee: "coinsacct111",
    issuer: session.actor,
    jsonmemo: "",
    memo: "Hello World!",
  },
}

async function main() {
  // Create a client connection to an available NATS server.
  const nc = await connect({
    servers: servers.split(","),
  });
  console.log(`servers ${servers} ${(performance.now()-startTime)/1000}`)
  let sub = nc.subscribe("local.nfcread");
  //console.log(`loading contractkit ${(performance.now()-startTime)/1000}`)
  //const contract = await contractKit.load("token.seeds")
  //const table = contract.table("stat")
  //console.log(`calling table ${(performance.now()-startTime)/1000}`)
  //const tresult = await table.get("", {
  //  scope: "SEEDS"
  //})
  //console.log(tresult)
  var nonce = 0
  console.log(`antelope.js NATS listening ${(performance.now()-startTime)/1000}`)
  for await (const msg of sub) {
    console.log(`${msg.string()} on subject ${msg.subject}`)
    badgeAction.data.memo = `Tag read ${msg.string()}`
    badgeAction.data.jsonmemo = `{ "nonce": ${nonce} }`
    nonce += 1
    console.log(`calling transact ${(performance.now()-startTime)/1000}`)
    const sresult = await session.transact({ action: badgeAction })
    console.log(`Transaction was successfully broadcast! ${(performance.now()-startTime)/1000}`)
    console.log(
      `Explorer Link: https://explorer.telos.net/transaction/${sresult.response.transaction_id}`
    )
  }
  console.log("left loop")
}

main()

