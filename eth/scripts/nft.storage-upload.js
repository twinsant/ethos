const { NFTStorage, File, Blob } = require('nft.storage');
const NFT_STORAGE_TOKEN = process.env.PRD_NFT_STORAGE_API_KEY;
const client = new NFTStorage({ token: NFT_STORAGE_TOKEN });

const imageFile = new File([ someBinaryImageData ], 'x.png', { type: 'image/png' })
const metadata = await client.store({
  name: 'My sweet NFT',
  description: 'Just try to funge it. You can\'t do it.',
  image: imageFile
})

// store a single binary data object
const someData1 = new Blob(["hello world"])
const cid1 = await client.storeBlob(someData)

// store a collection of files
const readmeFile = new File('Run node src/index.js for a friendly greeting.', 'README.txt', { type: 'text/plain' })
const sourceFile = new File('console.log("hello, world")', 'src/index.js', { type: 'text/javascript' })
const cid2 = await client.storeDirectory([readmeFile, sourcefile])

// store a Content Archive (CAR)
const someData2 = new Blob(["hello world"])
const { car } = await NFTStorage.encodeBlob(someData)
const cid = await client.storeCar(car)