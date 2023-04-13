function isValidStatus(status) {
  return (status >= 0) && (status < 4) ? true : false
}

function parseLocalization(localization) {
  return localization.replace('+','').split(',')
}

function isValidLocalization(localization) {
  const regex = /^[-+]?\d+(\.\d+)?$/;
  return regex.test(localization);
}

function decodeUplink(input) {
  let obj_data = JSON.parse(String.fromCharCode.apply(null, input.bytes))
  
  if (obj_data[0] == 1){
    return {
      warnings: [],
      data: {send_to_lambda: 'false', is_query: 'true'}
    }
  }
  
  // Reported data
  let reported_status = obj_data[1]
  let localization_data = parseLocalization(obj_data[2])
  
  // Validations
  let response = {
    data: {send_to_lambda: 'false', is_query: 'false'}
  }
  if (isValidStatus(reported_status)) {
    response = {
      ...response,
      data: {
        ...response.data,
        send_to_lambda: 'true',
        reported_status
      }
    }
  }else {
    return response
  }
  if (isValidLocalization(localization_data[0])&&isValidLocalization(localization_data[1])) {
    response.data = {
      ...response.data,
      localization_data
    }
  } else {
    response.data = {
      ...response.data,
      localization_data
    }
    response.warnings = [{
      message: "The localization isn't valid."
    }]
  }
  
  return response;
}