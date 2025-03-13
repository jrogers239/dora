import React, { createContext, useContext, useEffect, useState } from 'react';
import { auth } from '../firebase';
import { User, signInWithEmailAndPassword, signInAnonymously, onAuthStateChanged } from 'firebase/auth';

interface AuthContextType {
    user: User | null;
    loading: boolean;
    login: (email: string, password: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
    user: null,
    loading: true,
    login: async () => {}
});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const unsubscribe = onAuthStateChanged(auth, (user) => {
            if (user) {
                setUser(user);
            } else {
                // Sign in anonymously if no user
                signInAnonymously(auth)
                    .catch((error) => {
                        console.error("Anonymous auth error:", error);
                    });
            }
            setLoading(false);
        });

        return () => unsubscribe();
    }, []);

    const login = async (email: string, password: string) => {
        try {
            const userCredential = await signInWithEmailAndPassword(auth, email, password);
            const user = userCredential.user;

            // Call backend to store user in Redis
            await fetch('/api/storeUser', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ uid: user.uid, email: user.email }),
            });
        } catch (error) {
            console.error("Login error:", error);
        }
    };

    return (
        <AuthContext.Provider value={{ user, loading, login }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};
