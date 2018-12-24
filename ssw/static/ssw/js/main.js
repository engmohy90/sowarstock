function wrapCheckbox(checkboxId,wrapperId, labelText){
     $("label[for='"+checkboxId+"']").remove()
     $("#" + checkboxId).wrap('<div id="'+wrapperId+'" class="input-checkbox input-checkbox--switch"></div>').after('<label for="'+checkboxId+'"></label>')
     $("#"+wrapperId).before('<br>')
     $("#"+wrapperId).after('<span>'+labelText+'</span>')
}

function sendUplodResult(xhrjson, result, attemptNo, user){
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/ajax/upload_result?xhr="+xhrjson+"&result="+result+"&user="+user+"&attemptNo="+attemptNo);
  xhr.send();
}


function uploadProductImage(username){
    $("#image").change(function(){
        var input = $(this)
        var files = document.getElementById("image").files;
        var file = files[0];
        $("#image_loader").removeClass("hidden")
        $("#submit_product_button").prop("disabled",true)
        if(file){
            var extension = file.name.split(".").pop().toLowerCase()
            var size = file.size/1024/1024
            if(size < 50){
                if(extension == "jpg" || extension == "jpeg"){
                    var _URL = window.URL || window.webkitURL;
                    var img = new Image();
                    img.onload = function () {
                        var image_size_in_megapixels = (this.width * this.height) / 1000000
                        if(image_size_in_megapixels < 4){
                            alert("Image has to be at least 4 Megapixels")
                            input.val("")
                            $("#image_loader").addClass("hidden")
                            $("#submit_product_button").prop("disabled",false)
                            return
                        }else{
                            getImageSignedRequest(file, username);
                        }
                    };
                    img.src = _URL.createObjectURL(file);
                }else if(extension == "tiff"){
                    var reader = new FileReader()
                    reader.onload = function () {
                        var image_size_in_megapixels = (this.width * this.height) / 1000000
                        if(image_size_in_megapixels < 4){
                            alert("Image has to be at least 4 Megapixels")
                            input.val("")
                            $("#image_loader").addClass("hidden")
                            $("#submit_product_button").prop("disabled",false)
                            return
                        }else{
                            getImageSignedRequest(file, username);
                        }
                    }
                    reader.readAsArrayBuffer( file )
                }else{
                    alert("Image type has to be only jpeg or tiff")
                    input.val("")
                    $("#image_loader").addClass("hidden")
                    $("#submit_product_button").prop("disabled",false)
                    return
                }
            }else{
                alert("Image size has to be less than 50 MB")
                input.val("")
                $("#image_loader").addClass("hidden")
                $("#submit_product_button").prop("disabled",false)
                return
            }
        }
    })
}

function getImageSignedRequest(file, username){
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "/ajax/sign_s3?file_type="+file.type+"&destination=products");
  xhr.onreadystatechange = function(){
    if(xhr.readyState === 4){
      if(xhr.status === 200){
        var response = JSON.parse(xhr.responseText);
        uploadImageFile(file, response.data, response.url, 1, username);
      }
      else{
        alert("Oops! An error has occurred ! Please try again");
        $("#image_loader").addClass("hidden")
        $("#submit_product_button").prop("disabled",false)
      }
    }
  };
  xhr.send();
}

function uploadImageFile(file, s3Data, url, attemptNo, username){

  if(attemptNo < 6){
    var xhr = new XMLHttpRequest();
      xhr.open("POST", s3Data.url);

      var postData = new FormData();
      for(key in s3Data.fields){
        postData.append(key, s3Data.fields[key]);
      }
      postData.append('file', file);

      xhr.onreadystatechange = function() {
        if(xhr.readyState === 4){
          var xhrjson = {}
          for (var key in xhr){
                xhrjson[key] = xhr[key]
          }
          if(xhr.status === 200 || xhr.status === 204){
            document.getElementById("image_url").value = url;
            $("#image_loader").addClass("hidden")
            $("#submit_product_button").prop("disabled",false)
            sendUplodResult(JSON.stringify(xhrjson), "Success", attemptNo, username)
          }
          else{
            sendUplodResult(JSON.stringify(xhrjson), "SuccessFailure", attemptNo, username)
            var newAttempt = attemptNo + 1
            $("#image_error").html("Error while uploading the file. Trying again. Attempt: "+ newAttempt)
            uploadFile(file, s3Data, url, newAttempt)
          }

       }

      };
      xhr.send(postData);
  }else{
    $("#image_error").html("Could not upload the file. Please try again.")
    $("#image").val("")
    $("#image_url").val("")
  }

}

function uploadProductFile(username){
    $("#file").change(function(){
        var input = $(this)
        var files = document.getElementById("file").files;
        var file = files[0];
        $("#file_loader").removeClass("hidden")
        $("#submit_product_button").prop("disabled",true)

        if(file){
            var extension = file.name.split(".").pop().toLowerCase()

            if(extension == "eps"){
                var size = file.size/1024/1024

                if(size < 15){
                    getFileSignedRequest(file, extension, username);
                }else{
                    alert("File size has to be less than 15 MB")
                    input.val("")
                    $("#image_loader").addClass("hidden")
                    $("#submit_product_button").prop("disabled",false)
                    return
                }
            }else{
                alert("File type has to be eps")
                input.val("")
                $("#file_loader").addClass("hidden")
                $("#submit_product_button").prop("disabled",false)
                return
            }

        }
    })
}

function getFileSignedRequest(file,extension, username){
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "/ajax/sign_s3?file_type="+extension+"&destination=products");
  xhr.onreadystatechange = function(){
    if(xhr.readyState === 4){
      if(xhr.status === 200){
        var response = JSON.parse(xhr.responseText);
        uploadFileFile(file, response.data, response.url, 1, username);
      }
      else{
        alert("Oops! An error has occurred ! Please try again");
        $("#file_loader").addClass("hidden")
        $("#submit_product_button").prop("disabled",false)
      }
    }
  };
  xhr.send();
}

function uploadFileFile(file, s3Data, url, attemptNo, username){

  if(attemptNo < 6){
    var xhr = new XMLHttpRequest();
    xhr.open("POST", s3Data.url);

    var postData = new FormData();
    for(key in s3Data.fields){
      postData.append(key, s3Data.fields[key]);
    }
    postData.append('file', file);

    xhr.onreadystatechange = function() {
      if(xhr.readyState === 4){
        var xhrjson = {}
          for (var key in xhr){
                xhrjson[key] = xhr[key]
        }
        if(xhr.status === 200 || xhr.status === 204){
          document.getElementById("file_url").value = url;
          $("#file_loader").addClass("hidden")
          $("#submit_product_button").prop("disabled",false)
          sendUplodResult(JSON.stringify(xhrjson), "Success", attemptNo, username)
        }
        else{
          sendUplodResult(JSON.stringify(xhrjson), "Success", attemptNo, username)
          var newAttempt = attemptNo + 1
          $("#file_error").html("Error while uploading the file. Trying again. Attempt: "+ newAttempt)
          uploadFile(file, s3Data, url, newAttempt)
        }
      }
    };
      xhr.send(postData);
  }else{
     $("#file_error").html("Could not upload the file. Please try again.")
     $("#file").val("")
     $("#file_url").val("")
  }
}