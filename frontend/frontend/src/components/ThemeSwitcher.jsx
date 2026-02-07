import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Palette, Check } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

const themes = [
    { id: 'default', name: 'Kelp Dark', primary: '#0EA5E9', dark: '#0B1120' },
    { id: 'midnight', name: 'Midnight', primary: '#6366F1', dark: '#020617' },
    { id: 'emerald', name: 'Emerald', primary: '#10B981', dark: '#064E3B' },
    { id: 'sunset', name: 'Sunset', primary: '#F97316', dark: '#2D0F02' },
    { id: 'cyberpunk', name: 'Cyberpunk', primary: '#FF00FF', dark: '#1A0033' },
    { id: 'slate', name: 'Slate Blue', primary: '#64748B', dark: '#0F172A' },
    { id: 'amethyst', name: 'Amethyst', primary: '#8B5CF6', dark: '#1E1B4B' },
    { id: 'gold', name: 'Desert Gold', primary: '#EAB308', dark: '#1C1917' },
    { id: 'crimson', name: 'Crimson', primary: '#EF4444', dark: '#450A0A' },
    { id: 'mint', name: 'Mint Spruce', primary: '#2DD4BF', dark: '#0D2D2D' },
];


const ThemeSwitcher = () => {
    const { theme: currentTheme, setTheme } = useTheme();
    const [isOpen, setIsOpen] = useState(false);

    return (
        <div className="relative">
            <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setIsOpen(!isOpen)}
                className="p-2 rounded-full bg-white/5 border border-white/10 text-slate-400 hover:text-white hover:bg-white/10 transition-all flex items-center gap-2"
                title="Change Theme"
            >
                <Palette className="w-5 h-5" />
                <span className="text-xs font-medium hidden lg:inline">Theme</span>
            </motion.button>

            <AnimatePresence>
                {isOpen && (
                    <>
                        <div
                            className="fixed inset-0 z-40"
                            onClick={() => setIsOpen(false)}
                        />
                        <motion.div
                            initial={{ opacity: 0, y: 10, scale: 0.95 }}
                            animate={{ opacity: 1, y: 0, scale: 1 }}
                            exit={{ opacity: 0, y: 10, scale: 0.95 }}
                            className="absolute right-0 mt-3 w-64 glass-card p-4 z-50 shadow-2xl border-brand-primary/20"
                        >
                            <h3 className="text-sm font-bold mb-4 flex items-center gap-2">
                                <Palette className="w-4 h-4 text-brand-primary" />
                                Select Theme
                            </h3>
                            <div className="grid grid-cols-2 gap-2">
                                {themes.map((t) => (
                                    <motion.button
                                        key={t.id}
                                        whileHover={{ scale: 1.02 }}
                                        whileTap={{ scale: 0.98 }}
                                        onClick={() => {
                                            setTheme(t.id);
                                            setIsOpen(false);
                                        }}
                                        className={`p-2 rounded-lg border text-left transition-all relative overflow-hidden ${currentTheme === t.id
                                            ? 'border-brand-primary bg-brand-primary/10 shadow-lg shadow-brand-primary/5'
                                            : 'border-white/5 bg-white/5 hover:border-white/20'
                                            }`}
                                    >
                                        <div className="flex items-center gap-2">
                                            <div
                                                className="w-4 h-4 rounded-full border border-white/10 shadow-sm"
                                                style={{ background: `linear-gradient(135deg, ${t.primary}, ${t.dark})` }}
                                            />
                                            <span className="text-[10px] font-bold truncate uppercase tracking-wider">
                                                {t.name}
                                            </span>
                                            {currentTheme === t.id && (
                                                <Check className="w-3 h-3 text-brand-primary ml-auto" />
                                            )}
                                        </div>
                                    </motion.button>
                                ))}
                            </div>
                        </motion.div>
                    </>
                )}
            </AnimatePresence>
        </div>
    );
};

export default ThemeSwitcher;
