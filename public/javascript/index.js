const signin_form = document.querySelector(".form-container.signin");
const signup_form = document.querySelector(".form-container.signup");
const span_register = document.querySelector(".span-register");
const h3 = document.querySelector(".form-wrapper h3");
const back = document.querySelector(".back");
const input = document.querySelectorAll(".form-signup input");
const err_icon = document.querySelectorAll(".input-item img[alt='error']");

span_register.addEventListener("click", () => {
  signin_form.style.display = "none";
  h3.innerText = "SINGUP";
  signup_form.style.display = "block";
  for (let i = 0; i < 5; i++) {
    err_icon[i].style.display = "none";
  }
});

back.addEventListener("click", () => {
  signup_form.style.display = "none";
  h3.innerText = "SINGIN";
  signin_form.style.display = "block";
});

signup_form.addEventListener("submit", (e) => {
  console.log(`input[0]:${typeof input[0].value}`);
  console.log(`input[1]:${input[1].value}`);
  console.log(`input[2]:${input[2].value}`);
  for (let i = 0; i < 3; i++) {
    if (input[i].value == "") {
      err_icon[i].style.display = "block";
      e.preventDefault();
    }
  }
});
