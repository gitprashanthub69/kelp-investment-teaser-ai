import React from 'react';
import { Link } from 'react-router-dom';
import { Anchor } from 'lucide-react';

const Navbar = () => {
    return (
        <nav className="w-full bg-brand-dark/90 backdrop-blur-md border-b border-white/10 sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    <Link to="/" className="flex items-center space-x-2">
                        <Anchor className="h-8 w-8 text-brand-primary" />
                        <span className="text-xl font-bold bg-gradient-to-r from-brand-primary to-brand-accent bg-clip-text text-transparent">
                            Kelp AI
                        </span>
                    </Link>

                    <div className="hidden md:flex items-center space-x-8">
                        <Link to="/features" className="text-slate-300 hover:text-white transition-colors">Features</Link>
                        <Link to="/pricing" className="text-slate-300 hover:text-white transition-colors">Pricing</Link>
                        <Link to="/login" className="px-4 py-2 rounded-lg text-white hover:bg-white/10 transition-colors">
                            Login
                        </Link>
                        <Link to="/signup" className="btn-primary">
                            Get Started
                        </Link>
                    </div>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
