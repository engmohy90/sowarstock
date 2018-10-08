function wrapCheckbox(checkboxId,wrapperId, labelText){
     $("label[for='"+checkboxId+"']").remove()
     $("#" + checkboxId).wrap('<div id="'+wrapperId+'" class="input-checkbox input-checkbox--switch"></div>').after('<label for="'+checkboxId+'"></label>')
     $("#"+wrapperId).before('<br>')
     $("#"+wrapperId).after('<span>'+labelText+'</span>')
}