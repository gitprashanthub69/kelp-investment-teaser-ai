import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import ThemeSwitcher from '../components/ThemeSwitcher';

const Auth = ({ type }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const isLogin = type === 'login';

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const endpoint = isLogin ? '/api/v1/auth/token' : '/api/v1/auth/signup';
            const payload = isLogin
                ? new URLSearchParams({ username: email, password })
                : { email, password };

            const config = isLogin
                ? { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
                : {};

            const res = await axios.post(`http://localhost:8000${endpoint}`, payload, config);

            if (res.data.access_token) {
                localStorage.setItem('token', res.data.access_token);
                navigate('/dashboard');
            } else if (!isLogin) {
                // After signup, redirect to login or auto-login
                navigate('/login');
            }
        } catch (err) {
            console.error("Login failed:", err);
            if (err.response) {
                console.log("Error response:", err.response.data);
                console.log("Error status:", err.response.status);
            }
            setError(err.response?.data?.detail || 'An error occurred');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center pt-16 px-4 relative overflow-hidden">
            {/* Top Right Theme Switcher */}
            <div className="absolute top-6 right-6 z-50">
                <ThemeSwitcher />
            </div>

            {/* Background decorative elements */}
            <motion.div
                animate={{
                    scale: [1, 1.1, 1],
                    rotate: [0, 5, -5, 0]
                }}
                transition={{ duration: 10, repeat: Infinity }}
                className="absolute top-1/4 -left-20 w-80 h-80 bg-brand-primary/10 rounded-full blur-3xl -z-10"
            />
            <motion.div
                animate={{
                    scale: [1, 1.2, 1],
                    rotate: [0, -10, 10, 0]
                }}
                transition={{ duration: 12, repeat: Infinity }}
                className="absolute bottom-1/4 -right-20 w-96 h-96 bg-brand-accent/10 rounded-full blur-3xl -z-10"
            />

            <motion.div
                initial={{ opacity: 0, y: 30, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={{ duration: 0.6 }}
                className="glass-card w-full max-w-md p-8"
            >
                <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.2 }}
                    className="flex justify-center mb-6"
                >
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-brand-primary to-brand-accent flex items-center justify-center shadow-lg shadow-brand-primary/20">
                        <span className="font-bold text-white text-xl">K</span>
                    </div>
                </motion.div>

                <motion.h2
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="text-3xl font-bold mb-6 text-center"
                >
                    {isLogin ? 'Welcome Back' : 'Create Account'}
                </motion.h2>

                {error && (
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="mb-4 p-3 bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg text-sm"
                    >
                        {error}
                    </motion.div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.4 }}
                    >
                        <label className="block text-sm font-medium mb-1 text-slate-400">Email Address</label>
                        <input
                            type="email"
                            required
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="w-full bg-slate-800/50 border border-slate-700 rounded-lg px-4 py-2 focus:ring-2 focus:ring-brand-primary outline-none transition-all"
                            placeholder="you@company.com"
                        />
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.5 }}
                    >
                        <label className="block text-sm font-medium mb-1 text-slate-400">Password</label>
                        <input
                            type="password"
                            required
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full bg-slate-800/50 border border-slate-700 rounded-lg px-4 py-2 focus:ring-2 focus:ring-brand-primary outline-none transition-all"
                            placeholder="••••••••"
                        />
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.6 }}
                    >
                        <motion.button
                            type="submit"
                            disabled={loading}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            className="w-full btn-primary py-3 disabled:opacity-50 disabled:cursor-not-allowed shadow-xl shadow-brand-primary/10"
                        >
                            {loading ? (
                                <span className="flex items-center justify-center gap-2">
                                    <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    Processing...
                                </span>
                            ) : (isLogin ? 'Sign In' : 'Sign Up')}
                        </motion.button>
                    </motion.div>
                </form>

                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.7 }}
                    className="mt-6 text-center text-sm text-slate-400"
                >
                    {isLogin ? "Don't have an account? " : "Already have an account? "}
                    <Link
                        to={isLogin ? '/signup' : '/login'}
                        className="text-brand-primary hover:text-brand-accent font-medium transition-colors"
                    >
                        {isLogin ? 'Sign Up' : 'Log In'}
                    </Link>
                </motion.div>
            </motion.div>
        </div>
    );
};

export default Auth;
