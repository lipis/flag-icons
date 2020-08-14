const path = require('path');
const fs = require('fs');
const chunk = require('lodash.chunk');
const sharp = require('sharp');
const imagemin = require('imagemin');
const imageminPngquant = require('imagemin-pngquant');
const { getCodes } = require('./index.js');

// Loops through all ISO country codes, opens corresponding SVG file, converts to buffer, resizes it.
// Returns an array of objects with the resized buffer and iso name
const buildBuffers = async (aspectRatio, width) => {
  try {
    const countryCodes = getCodes();
    const buffers = await Promise.all(
      countryCodes.map(async (countryCode) => {
        const flagSvg = path.join(`/flags/${aspectRatio}`, `${countryCode.toLowerCase()}.svg`);
        const flagBuffer = fs.readFileSync(path.join(__dirname, flagSvg));
        const resizedBuffer = await sharp(flagBuffer)
          .resize({ width })
          .png()
          .toBuffer();

        return {
          code: countryCode.toLowerCase(),
          buffer: resizedBuffer,
        };
      }),
    );
    return buffers;
  } catch (err) {
    throw new Error(err);
  }
};

const buildPngs = async (userOptions) => {
  const options = {
    width: 32,
    aspectRatio: '4x3', // 4x3 or 1x1
    get outputDir() { return `flags/${this.aspectRatio}/png` },
    ...userOptions,
  };

  try {
    fs.mkdirSync(path.join(__dirname, options.outputDir), { recursive: true }); // create the output dir

    const buffers = await buildBuffers(options.aspectRatio, options.width);
    await Promise.all(
      buffers.map(async (country) => {
        try {
          const pngFile = await sharp(country.buffer)
            .png()
            .toFile(path.join(__dirname, `${options.outputDir}/${country.code}.png`))
        } catch (err) {
          console.error(err);
        }
      })
    );
    console.log('PNGs built successfully');
  } catch (err) {
    console.error(err);
  }
};


const buildSprite = async (userOptions) => {
  const options = {
    width: 32,
    aspectRatio: '4x3', // 4x3 or 1x1
    get outputDir() { return `flags/sprite/${this.aspectRatio}`; },
    get outputFilename() { return `flag-sprite-${this.width}.png`; },
    ...userOptions,
  };

  const aspectMultiplier = options.aspectRatio === '4x3' ? 0.75 : 1;
  const flagHeight = options.width * aspectMultiplier;

  // create the output dir
  fs.mkdirSync(path.join(__dirname, options.outputDir), { recursive: true });

  async function buildSpritePiece(countries, portionIndex) {
    const spriteBuffers = countries.map((country, index) => {
      return {
        input: country.buffer,
        top: index * flagHeight,
        left: 0,
      };
    });

    try {
      fs.mkdirSync(path.join(__dirname, `${options.outputDir}/temp/${options.outputFilename}/`), { recursive: true });

      await sharp({
        create: {
          width: options.width,
          height: spriteBuffers.length * flagHeight,
          channels: 3,
          background: { r: 255, g: 0, b: 0 },
        },
      })
        .composite(spriteBuffers) // the flags get placed here
        .png()
        .toFile(path.join(__dirname, `${options.outputDir}/temp/${options.outputFilename}/sprite-piece-${portionIndex}.png`));
      // console.log(`build sprite piece ${portionIndex}`);
    } catch (err) {
      throw new Error(err);
    }
  }

  async function combineFinalSprite(flagsPerChunk, numberOfChunks, spriteTotalHeight) {
    const spritePieces = [];
    for (let i = 0; i < numberOfChunks; ++i) {
      spritePieces.push({
        input: path.join(__dirname, `${options.outputDir}/temp/${options.outputFilename}/sprite-piece-${i}.png`),
        top: flagHeight * flagsPerChunk * i,
        left: 0,
      });
    }
    try {
      await sharp({
        create: {
          width: options.width,
          height: spriteTotalHeight,
          channels: 3,
          background: { r: 255, g: 0, b: 0 },
        },
      })
        .composite(spritePieces) // combine the sprite pieces
        .png()
        .toFile(path.join(__dirname, `${options.outputDir}/${options.outputFilename}`));

      // optimize images
      await imagemin([path.join(__dirname, `${options.outputDir}/${options.outputFilename}`)], {
        destination: path.join(__dirname, `${options.outputDir}`),
        plugins: [
          imageminPngquant()
        ]
      });

      console.log('built final sprite');
    } catch (err) {
      throw new Error(err);
    }
  }

  try {
    // We have it to build the sprite in pieces since we can run out of memory otherwise.
    fs.mkdirSync(path.join(__dirname, `${options.outputDir}/temp`), { recursive: true });

    const buffers = await buildBuffers(options.aspectRatio, options.width);
    const flagsPerChunk = 5;
    const bufferChunks = chunk(buffers, flagsPerChunk);

    Promise.all(
      bufferChunks.map(async (bufferChunk, index) => {
        try {
          await buildSpritePiece(bufferChunk, index);
        } catch (err) {
          throw new Error(err);
        }
      }),
    );
    const numberOfChunks = bufferChunks.length;
    const spriteTotalHeight = buffers.length * flagHeight;
    await combineFinalSprite(flagsPerChunk, numberOfChunks, spriteTotalHeight);

    // clean up temp directory
    fs.rmdirSync(path.join(__dirname, `${options.outputDir}/temp`), { recursive: true });
  } catch (err) {
    throw new Error(err);
  }
};

(async function () {
  try {
    // await buildPngs({ width: 32, aspectRatio: '4x3'});
    // await buildPngs({ width: 32, aspectRatio: '1x1'});
    await buildSprite({ width: 32, aspectRatio: '4x3', outputFilename: 'flag-sprite-32.png' });
    await buildSprite({ width: 64, aspectRatio: '4x3', outputFilename: 'flag-sprite-32_2x.png' });
    await buildSprite({ width: 32, aspectRatio: '1x1', outputFilename: 'flag-sprite-32.png' });
    await buildSprite({ width: 64, aspectRatio: '1x1', outputFilename: 'flag-sprite-32_2x.png' });
  } catch (err) {
    console.error(err);
  }
})();
