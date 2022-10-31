
function signup(){
  let nameRegi = document.querySelector("#name1");
  let uNameRegi = document.querySelector("#username1");
  let pwdRegi = document.querySelector("#password1");
  fetch("/signup", {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      "name": nameRegi.value,
      "username": uNameRegi.value,
      "password": pwdRegi.value
    }),
  })
  .then((response) => response.json())
  .then((data) => {
    if(data.result == "OK"){
      alert("帳號創建成功");
      window.location.href="/";

    } else if (data.result == "請輸入註冊資訊"){
      alert("請輸入註冊資訊");
      
    } else if (data.result == "帳號已存在"){
      window.location.href="/error?message=帳號已經被註冊";
    }
  })
}

function signin(){
  let uNameRegi = document.querySelector("#username2");
  let pwdRegi = document.querySelector("#password2");
  fetch("/signin", {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      "username": uNameRegi.value,
      "password": pwdRegi.value
    }),
  })
  .then((response) => response.json())
  .then((data) => {
    if(data.result == "OK"){
      window.location.href="/member";

    } else if (data.result == "請輸入登入資訊"){
      alert("請輸入登入資訊");

    } else if (data.result == "帳號或密碼輸入錯誤"){
      window.location.href="/error?message=帳號或密碼輸入錯誤";
    }
  })
}