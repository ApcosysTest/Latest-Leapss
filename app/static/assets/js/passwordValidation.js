//Password Validation

function spChars(str) {
    var re = /^.*(?=.{2,})(?=.*[@#$%^&+=]).*$/;
    return re.test(str);
}
function nums(str) {
    var re = /^.*(?=.{2,})(?=.*[0-9]).*$/;
    return re.test(str);
}
function upperCases(str) {
    var re = /^.*(?=.{2,})(?=.*[A-Z]).*$/;
    return re.test(str);
}
function chars(str) {
    var re = /^.{8,}$/;
    return re.test(str);
}
function validatepass(e){
    var username = document.getElementById('id_username').value;
    var password = document.getElementById('id_password1').value;

    var spChar = spChars(password)  
    var num = nums(password)
    var upperCase = upperCases(password) 
    var char = chars(password) 

    if(e.key === 'Backspace'){ 
        document.getElementById('ir1').checked  = false;
        document.getElementById('ir3').checked  = false;
        document.getElementById('ir4').checked  = false;
    }
    if (char === true){ 
        document.getElementById('ir1').checked  = true; 
    } 
    else{ 
        document.getElementById('ir1').checked  = false; 
    }
    if (spChar === true){ 
        document.getElementById('ir4').checked  = true; 
    } 
    else{ 
        document.getElementById('ir4').checked  = false; 
    }
    if (num === true){ 
        document.getElementById('ir2').checked  = true; 
    } 
    else{ 
        document.getElementById('ir2').checked  = false; 
    }
    if (upperCase === true){ 
        document.getElementById('ir5').checked  = true; 
    } 
    else{ 
        document.getElementById('ir5').checked  = false; 
    }

    var perc=Math.round(similarity(username,password)*10000)/100; 
    if (perc < 60){
        document.getElementById('ir3').checked  = true; 
    } 
    else{
        document.getElementById('ir3').checked  = false;

    }  
}
function handleFocus() {
    var helpertext = document.getElementsByClassName('helpertext');
    if (helpertext.length > 0) {
        helpertext[0].style.display = "block";
    }
}
function handleBlur() {
    var helpertext = document.getElementsByClassName('helpertext');
    if (helpertext.length > 0) {
        helpertext[0].style.display = "none";
    }
}
function similarity(username,password){
    var longer = username;
        var shorter = password;
        if (username.length < password.length) {
          longer = password;
          shorter = username;
        }
        var longerLength = longer.length;
        if (longerLength === 0) {
            sim = 1.0;
        }
        return( longerLength - editDistance(longer, shorter)) / parseFloat(longerLength);
}

function editDistance(s1, s2) {
    s1 = s1.toLowerCase();
    s2 = s2.toLowerCase();
  
    var costs = new Array();
    for (var i = 0; i <= s1.length; i++) {
      var lastValue = i;
      for (var j = 0; j <= s2.length; j++) {
        if (i == 0)
          costs[j] = j;
        else {
          if (j > 0) {
            var newValue = costs[j - 1];
            if (s1.charAt(i - 1) != s2.charAt(j - 1))
              newValue = Math.min(Math.min(newValue, lastValue),
                costs[j]) + 1;
            costs[j - 1] = lastValue;
            lastValue = newValue;
          }
        }
      }
      if (i > 0)
        costs[s2.length] = lastValue;
    }
    return costs[s2.length];
  } 

//   Confirm Password 

function validate_password() {  
    var pass = document.getElementById('id_password1').value;
    var confirm_pass = document.getElementById('id_password2').value;
    if (pass != confirm_pass) {
        document.getElementById('wrong_pass_alert').style.color = 'red';
        document.getElementById('wrong_pass_alert').innerHTML
          = '☒ Use same password';
    } else {
        if (confirm_pass == '')
        {
            document.getElementById('wrong_pass_alert').innerHTML ='&nbsp;';   
        }
        else {
            document.getElementById('wrong_pass_alert').style.color = 'green';
            document.getElementById('wrong_pass_alert').innerHTML =
            '🗹 Password Matched';
        }
    }
   }
   
   function wrong_pass_alert() {
    if (document.getElementById('Password').value != document.getElementById('Confirm_Password').value) {
        alert("Password not Matched");
    } 
   }