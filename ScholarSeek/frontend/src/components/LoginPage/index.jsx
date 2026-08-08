import logo from '../../assets/Images/logo.png'
import {useNavigate} from 'react-router-dom'
import './LoginPage.css'

function LoginPage() {
  const navigate = useNavigate();
  const togglePassword = (event) => {
    const passwordInput = document.getElementById('passweord');
    if (event.target.checked) {
      passwordInput.type = 'text';
    } else {
      passwordInput.type = 'password';
    }
  }

  const formSubmitted = async (event) => {
    event.preventDefault();
    const form = document.getElementById('login-form');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    form.reset();
    try {
      console.log('Submitting login request with data:', data);
      const response = await fetch('http://localhost:3000/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      console.log('Response status:', response );
      if (response.ok) {
        localStorage.setItem('jwtoken', await response.text());
        navigate('/'); 
      } else {
        const error = await response.text();
        console.error('Error registering user:', error);
        alert(`Login failed: ${error}`);
      }
    } catch (error) {
      console.error('Network error:', error);
      alert('Network error, please try again later.');
    }
  }

  return (
    <>
      <div className="login-container">
        <div>
          <img src={logo} alt="Sholarseek Logo" className="logo" />
        </div>
        <form id="login-form" onSubmit={formSubmitted}>
            <div className="form-group">
                <label htmlFor="username" className="form-label">USERNAME</label>
                <input type="text" className="form-input" id="username" name="username" placeholder="Username" required />
            </div>
            <div className="form-group">
                <label htmlFor="password" className="form-label">PASSWORD</label>
                <input type="password" id="passweord" className="form-input" name="password" placeholder="Password" required />
            </div>
            <div className="checkbox-container">
                <input type="checkbox" className="checkbox" id="showpassword" onChange={togglePassword} />
                <label htmlFor="showpassword" className="checkbox-label">Show Password</label>
            </div>
            <button type="Submit" className="login-button">Login</button>
        </form>
      </div>
      <div className="login-footer">
        <p>Don't have an account? <a href="/register">Register</a></p>
      </div>
    </>
  )
}

export default LoginPage
