import React, { useState } from 'react';
import Login from './Login';
import SignUp from './SignUp';
import '../../css/auth.css';

export type AuthMode = 'login' | 'signup';

const Auth: React.FC = () => {
    const [mode, setMode] = useState<AuthMode>('login');

    const toggleMode = () => {
        setMode(mode === 'login' ? 'signup' : 'login');
    };

    return (
        <div className="auth-container">
            <div className="auth-box">
                {mode === 'login' ? (
                    <>
                        <Login />
                        <button onClick={toggleMode} className="auth-link">
                            Don't have an account? Sign up
                        </button>
                    </>
                ) : (
                    <>
                        <SignUp />
                        <button onClick={toggleMode} className="auth-link">
                            Already have an account? Log in
                        </button>
                    </>
                )}
            </div>
        </div>
    );
};

export default Auth;
