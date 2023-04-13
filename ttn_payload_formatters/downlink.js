function toByteArray(intArray) {
    let byteArray = [];
  
    for (let i = 0; i < intArray.length; i++) {
      let int32 = intArray[i];
      for (let j = 0; j < 4; j++) {
        byteArray.push((int32 >> (j * 8)) & 0xff);
      }
    }
    return byteArray;
  }
  
  function encodeDownlink(input) {
    return {
      bytes: toByteArray(input.Items),
      fPort: 1,
      warnings: [],
      errors: []
    };
  }
  
  function decodeDownlink(input) {
    return {
      data: {
        bytes: input.bytes
      },
      warnings: [],
      errors: []
    }
  }