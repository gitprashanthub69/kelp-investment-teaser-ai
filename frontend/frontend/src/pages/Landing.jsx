import React from 'react';
import { motion } from 'framer-motion';
import {
    ArrowRight, CheckCircle, Shield, Zap, FileText, Globe,
    BarChart2, Lock, Cpu, Layers, Activity, Database, Share2
} from 'lucide-react';
import { Link } from 'react-router-dom';
import ThemeSwitcher from '../components/ThemeSwitcher';

const Landing = () => {
    return (
        <div className="min-h-screen overflow-hidden">
            <Navbar />
            <Hero />
            <ProblemSection />
            <SolutionWorkflow />
            <SectorIntelligence />
            <AnonymizationFeature />
            <VisualIntelligence />
            <OutputPreview />
            <TrustSection />
            <CallToAction />
            <Footer />
        </div>
    );
};

// --- Sub-Components ---

const Navbar = () => (
    <motion.nav
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="fixed w-full z-50 bg-brand-dark/80 backdrop-blur-lg border-b border-white/5"
    >
        <div className="max-w-7xl mx-auto px-6 h-20 flex justify-between items-center">
            <div className="flex items-center gap-2">
                <motion.div
                    whileHover={{ scale: 1.1, rotate: 5 }}
                    className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-primary to-brand-accent flex items-center justify-center cursor-pointer"
                >
                    <span className="font-bold text-white text-lg">K</span>
                </motion.div>
                <span className="text-xl font-display font-bold text-white">Kelp AI</span>
            </div>
            <div className="hidden md:flex items-center gap-8">
                {["Why Kelp", "Solution", "Pricing"].map((item) => (
                    <motion.a
                        key={item}
                        href={`#${item.toLowerCase().split(' ')[0]}`}
                        whileHover={{ y: -2 }}
                        className="text-sm font-medium text-slate-300 hover:text-white transition-colors"
                    >
                        {item}
                    </motion.a>
                ))}
            </div>
            <div className="flex items-center gap-4">
                <ThemeSwitcher />
                <motion.div
                    whileHover={{ scale: 1.05 }}
                    className="hidden md:flex items-center gap-2 cursor-pointer text-slate-400 hover:text-white text-sm"
                >
                    <Globe className="w-4 h-4" />
                    <span>EN</span>
                </motion.div>
                <Link to="/login">
                    <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} className="btn-secondary py-2 px-4 text-sm">Login</motion.button>
                </Link>
                <Link to="/signup">
                    <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} className="btn-primary py-2 px-4 text-sm">Signup</motion.button>
                </Link>
            </div>
        </div>
    </motion.nav>
);

const Hero = () => {
    const text1 = "Automate Investment ";
    const text2 = "Teasers in Minutes";

    return (
        <section className="relative pt-32 pb-20 px-6 overflow-hidden">
            {/* Background Glows with Animation */}
            <motion.div
                animate={{
                    scale: [1, 1.2, 1],
                    opacity: [0.15, 0.25, 0.15]
                }}
                transition={{
                    duration: 8,
                    repeat: Infinity,
                    ease: "easeInOut"
                }}
                className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[800px] bg-brand-primary/10 rounded-full blur-[120px] -z-10"
            />

            <div className="max-w-7xl mx-auto text-center">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                    className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 mb-8"
                >
                    <span className="w-2 h-2 rounded-full bg-brand-accent animate-pulse" />
                    <span className="text-sm text-brand-accent font-medium">New: Enterprise Sector Models</span>
                </motion.div>

                <motion.h1
                    initial="hidden"
                    animate="visible"
                    className="text-5xl md:text-7xl font-bold mb-6 leading-tight flex flex-wrap justify-center relative z-10"
                >
                    {text1.trim().split(" ").map((word, wi, words) => (
                        <span key={`w1-${wi}`} className="inline-flex mr-4 last:mr-0">
                            {word.split("").map((char, ci) => {
                                const index = words.slice(0, wi).join(" ").length + (wi > 0 ? 1 : 0) + ci;
                                return (
                                    <motion.span
                                        key={`c1-${index}`}
                                        variants={{
                                            hidden: { opacity: 0, y: 10 },
                                            visible: {
                                                opacity: 1,
                                                y: [0, -8, 0],
                                                transition: {
                                                    y: { repeat: Infinity, duration: 3, ease: "easeInOut", delay: index * 0.05 },
                                                    opacity: { duration: 0.5, delay: index * 0.05 }
                                                }
                                            }
                                        }}
                                        className="inline-block"
                                    >
                                        {char}
                                    </motion.span>
                                );
                            })}
                        </span>
                    ))}
                    <div className="w-full h-0" />
                    {text2.trim().split(" ").map((word, wi, words) => (
                        <span key={`w2-${wi}`} className="inline-flex mr-4 last:mr-0 text-brand-primary">
                            {word.split("").map((char, ci) => {
                                const index = text1.length + words.slice(0, wi).join(" ").length + (wi > 0 ? 1 : 0) + ci;
                                return (
                                    <motion.span
                                        key={`c2-${index}`}
                                        variants={{
                                            hidden: { opacity: 0, y: 10 },
                                            visible: {
                                                opacity: 1,
                                                y: [0, -8, 0],
                                                transition: {
                                                    y: { repeat: Infinity, duration: 3, ease: "easeInOut", delay: index * 0.05 },
                                                    opacity: { duration: 0.5, delay: index * 0.05 }
                                                }
                                            }
                                        }}
                                        className="inline-block"
                                    >
                                        {char}
                                    </motion.span>
                                );
                            })}
                        </span>
                    ))}
                </motion.h1>

                <motion.p
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.7, delay: 0.4 }}
                    className="text-xl text-slate-400 mb-10 max-w-2xl mx-auto"
                >
                    Transform scattered private data into anonymized, investor-ready PowerPoint presentations with enterprise-grade AI.
                </motion.p>

                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.7, delay: 0.6 }}
                    className="flex flex-col sm:flex-row gap-4 justify-center"
                >
                    <Link to="/signup">
                        <motion.button
                            whileHover={{ scale: 1.05, boxShadow: "0 0 20px rgba(14, 165, 233, 0.4)" }}
                            whileTap={{ scale: 0.95 }}
                            className="btn-primary"
                        >
                            Signup <ArrowRight className="w-5 h-5" />
                        </motion.button>
                    </Link>
                    <Link to="/login">
                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="btn-secondary"
                        >
                            Login
                        </motion.button>
                    </Link>
                </motion.div>

                {/* Triple 3D Showcase */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-24 relative max-w-6xl mx-auto px-4">
                    <DataStack3D />
                    <DealStack3D />
                    <SecurityShield3D />
                </div>
            </div>
        </section>
    );
};

const DealStack3D = () => (
    <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 1, delay: 0.8 }}
        className="relative h-[400px]"
        style={{ perspective: "1200px" }}
    >
        <div className="flex items-center justify-center h-full">
            {[1, 2, 3].map((item, i) => (
                <motion.div
                    key={item}
                    animate={{
                        rotateY: [20, 30, 20],
                        rotateX: [10, 0, 10],
                        y: [i * -30, i * -30 - 10, i * -30],
                        z: i * 40
                    }}
                    transition={{
                        duration: 6,
                        repeat: Infinity,
                        ease: "easeInOut",
                        delay: i * 0.8
                    }}
                    className="absolute w-44 h-56 rounded-xl glass-card p-4 border-brand-primary/20 shadow-2xl flex flex-col justify-between"
                    style={{
                        transformStyle: "preserve-3d",
                        backdropFilter: "blur(12px)",
                        zIndex: 10 - i
                    }}
                >
                    <div className="flex justify-between items-start">
                        <Zap className="text-brand-primary h-4 w-4" />
                        <div className="h-2 w-8 bg-white/5 rounded" />
                    </div>
                    <div className="space-y-2">
                        <div className="h-2 w-3/4 bg-white/10 rounded" />
                        <div className="h-1.5 w-full bg-white/5 rounded" />
                    </div>
                </motion.div>
            ))}
        </div>
        <p className="absolute bottom-0 w-full text-center text-xs font-bold text-slate-500 tracking-widest uppercase">Deal Flow Engine</p>
    </motion.div>
);

const DataStack3D = () => (
    <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 1, delay: 1 }}
        className="relative h-[400px]"
        style={{ perspective: "1200px" }}
    >
        <div className="flex items-center justify-center h-full">
            {[1, 2, 3].map((item, i) => (
                <motion.div
                    key={item}
                    animate={{
                        rotateY: [-20, -30, -20],
                        rotateX: [10, 0, 10],
                        y: [i * -30, i * -30 - 10, i * -30],
                        z: i * 40
                    }}
                    transition={{
                        duration: 5,
                        repeat: Infinity,
                        ease: "easeInOut",
                        delay: i * 0.5
                    }}
                    className="absolute w-44 h-56 rounded-xl glass-card p-4 border-brand-accent/20 shadow-2xl"
                    style={{
                        transformStyle: "preserve-3d",
                        backdropFilter: "blur(12px)",
                        zIndex: 10 - i
                    }}
                >
                    <div className="flex justify-between items-start mb-4">
                        <BarChart2 className="text-brand-accent h-4 w-4" />
                        <Activity className="text-slate-500 h-3 w-3 animate-pulse" />
                    </div>
                    <div className="space-y-3">
                        {[1, 2, 3, 4].map(line => (
                            <div key={line} className="flex items-end gap-1 h-8">
                                <motion.div animate={{ height: [10, 20, 10] }} transition={{ duration: 2, repeat: Infinity, delay: line * 0.2 }} className="w-2 bg-brand-accent/30 rounded-t-sm" />
                                <motion.div animate={{ height: [15, 25, 15] }} transition={{ duration: 2, repeat: Infinity, delay: line * 0.3 }} className="w-2 bg-brand-accent/50 rounded-t-sm" />
                                <motion.div animate={{ height: [8, 18, 8] }} transition={{ duration: 2, repeat: Infinity, delay: line * 0.4 }} className="w-2 bg-brand-accent/20 rounded-t-sm" />
                            </div>
                        ))}
                    </div>
                </motion.div>
            ))}
        </div>
        <p className="absolute bottom-0 w-full text-center text-xs font-bold text-slate-500 tracking-widest uppercase">Market Intelligence</p>
    </motion.div>
);

const SecurityShield3D = () => (
    <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 1, delay: 1.2 }}
        className="relative h-[400px]"
        style={{ perspective: "1200px" }}
    >
        <div className="flex items-center justify-center h-full relative">
            {/* Orbital Rings */}
            {[1, 2, 3].map((ring, i) => (
                <motion.div
                    key={ring}
                    animate={{
                        rotateZ: [0, 360],
                        rotateX: [60, 60],
                        rotateY: [i * 30, i * 30]
                    }}
                    transition={{
                        duration: 10 + (i * 5),
                        repeat: Infinity,
                        ease: "linear"
                    }}
                    className="absolute w-48 h-48 rounded-full border border-brand-primary/20"
                    style={{ transformStyle: "preserve-3d" }}
                />
            ))}

            <motion.div
                animate={{
                    scale: [1, 1.1, 1],
                    rotateY: [0, 360]
                }}
                transition={{
                    duration: 8,
                    repeat: Infinity,
                    ease: "easeInOut"
                }}
                className="w-32 h-32 rounded-3xl glass-card flex items-center justify-center border-brand-primary/40 shadow-[0_0_50px_rgba(14,165,233,0.3)]"
                style={{ transformStyle: "preserve-3d" }}
            >
                <Lock className="w-12 h-12 text-brand-primary" />
            </motion.div>

            {/* Pulsing Core */}
            <div className="absolute w-16 h-16 bg-brand-primary/20 rounded-full blur-2xl animate-pulse" />
        </div>
        <p className="absolute bottom-0 w-full text-center text-xs font-bold text-slate-500 tracking-widest uppercase">Blind Anonymization</p>
    </motion.div>
);

const ProblemSection = () => (
    <section id="problem" className="section-padding relative">
        <div className="text-center mb-16">
            <motion.h2
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                className="text-3xl md:text-5xl font-bold mb-6 flex flex-wrap justify-center"
            >
                {`The "Deal-Killers" of M&A`.split(" ").map((word, wi, words) => (
                    <span key={wi} className={`inline-flex mr-3 last:mr-0 ${wi >= 1 ? 'text-brand-primary' : ''}`}>
                        {word.split("").map((char, ci) => {
                            const index = words.slice(0, wi).join(" ").length + (wi > 0 ? 1 : 0) + ci;
                            return (
                                <motion.span
                                    key={index}
                                    variants={{
                                        hidden: { opacity: 0, y: 10 },
                                        visible: {
                                            opacity: 1,
                                            y: [0, -5, 0],
                                            transition: {
                                                y: { repeat: Infinity, duration: 3, ease: "easeInOut", delay: index * 0.05 },
                                                opacity: { duration: 0.5, delay: index * 0.05 }
                                            }
                                        }
                                    }}
                                    className="inline-block"
                                >
                                    {char}
                                </motion.span>
                            );
                        })}
                    </span>
                ))}
            </motion.h2>
            <motion.p
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.2 }}
                className="text-slate-400 text-lg max-w-2xl mx-auto"
            >
                Manual teaser creation is slow, error-prone, and burns junior banker hours.
            </motion.p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6" style={{ perspective: "1000px" }}>
            {[
                { icon: <FileText />, title: "Data Chaos", desc: "Financials buried in PDFs and Excel sheets." },
                { icon: <Cpu />, title: "Manual Extraction", desc: "Hours spent copy-pasting revenue tables." },
                { icon: <Lock />, title: "Privacy Risks", desc: "Accidental leaks of company identity." },
                { icon: <Layers />, title: "Compliance", desc: "Missing citations and audit trails." },
            ].map((item, i) => (
                <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 40 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.1, duration: 0.5 }}
                    whileHover={{
                        y: -10,
                        rotateX: 5,
                        rotateY: -5,
                        backgroundColor: "rgba(255, 255, 255, 0.08)",
                        borderColor: "rgba(14, 165, 233, 0.3)",
                        boxShadow: "0 20px 40px rgba(0,0,0,0.4)"
                    }}
                    className="glass-card p-8 transition-colors cursor-default group"
                    style={{ transformStyle: "preserve-3d" }}
                >
                    <motion.div
                        whileHover={{ scale: 1.1, rotate: 10 }}
                        className="w-12 h-12 rounded-lg bg-slate-700/50 flex items-center justify-center text-slate-300 mb-6 group-hover:bg-brand-primary/20 group-hover:text-brand-primary transition-colors"
                    >
                        {item.icon}
                    </motion.div>
                    <h3 className="text-xl font-bold mb-3">{item.title}</h3>
                    <p className="text-slate-400 leading-relaxed">{item.desc}</p>
                </motion.div>
            ))}
        </div>
    </section>
);

const SolutionWorkflow = () => (
    <section id="solution" className="section-padding">
        <div className="max-w-4xl mx-auto">
            <div className="text-center mb-16">
                <motion.span
                    initial={{ opacity: 0 }}
                    whileInView={{ opacity: 1 }}
                    className="text-brand-accent font-medium tracking-wider uppercase text-sm"
                >
                    The Workflow
                </motion.span>
                <motion.h2
                    initial={{ opacity: 0, y: 10 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    className="text-3xl md:text-4xl font-bold mt-2"
                >
                    From Raw Data to Deal Teaser
                </motion.h2>
            </div>

            <div className="relative">
                <motion.div
                    initial={{ height: 0 }}
                    whileInView={{ height: "100%" }}
                    transition={{ duration: 1.5, ease: "easeInOut" }}
                    className="absolute left-[20px] top-0 bottom-0 w-0.5 bg-gradient-to-b from-brand-primary/50 to-transparent md:left-1/2 md:-translate-x-1/2"
                />

                {[
                    { step: "01", title: "Upload Data Pack", desc: "Drag & drop CIMS, financials (Excel), and organization charts." },
                    { step: "02", title: "AI Extraction & Enrichment", desc: "Kelp extracts key metrics and enriches with web-scraped market positioning." },
                    { step: "03", title: "Smart Anonymization", desc: "Names, emails, and locations are auto-redacted and replaced with generic terms." },
                    { step: "04", title: "Generate Teaser", desc: "Download a fully branded, editable PowerPoint & Citation log." },
                ].map((item, i) => (
                    <motion.div
                        key={i}
                        initial={{ opacity: 0, x: i % 2 === 0 ? -50 : 50 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ margin: "-100px" }}
                        transition={{ duration: 0.6, delay: 0.2 }}
                        className={`relative flex items-center gap-8 mb-12 ${i % 2 === 0 ? 'md:flex-row' : 'md:flex-row-reverse'}`}
                    >
                        <div className="hidden md:block w-1/2" />
                        <motion.div
                            whileInView={{ scale: [0, 1.2, 1] }}
                            transition={{ duration: 0.5, delay: 0.5 }}
                            className="absolute left-0 md:left-1/2 md:-translate-x-1/2 w-10 h-10 rounded-full bg-brand-dark border-2 border-brand-primary flex items-center justify-center z-10 font-bold text-brand-primary text-sm shadow-[0_0_15px_rgba(14,165,233,0.5)]"
                        >
                            {item.step}
                        </motion.div>
                        <div className="w-full md:w-1/2 pl-12 md:pl-0 md:px-12">
                            <motion.div
                                whileHover={{ scale: 1.02, x: i % 2 === 0 ? 5 : -5 }}
                                className="glass-card p-6 border-l-4 border-l-brand-primary"
                            >
                                <h3 className="text-xl font-bold mb-2">{item.title}</h3>
                                <p className="text-slate-400 text-sm">{item.desc}</p>
                            </motion.div>
                        </div>
                    </motion.div>
                ))}
            </div>
        </div>
    </section>
);

const SectorIntelligence = () => (
    <section className="section-padding bg-white/5 relative overflow-hidden rounded-3xl my-20 mx-4 md:mx-0">
        <motion.div
            animate={{
                rotate: 360,
                x: [0, 50, -50, 0],
                y: [0, -50, 50, 0]
            }}
            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            className="absolute -right-20 -top-20 w-96 h-96 bg-brand-accent/10 rounded-full blur-3xl -z-10"
        />

        <div className="text-center mb-16">
            <motion.h2
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                className="text-3xl md:text-5xl font-bold mb-4"
            >
                Sector-Aware Intelligence
            </motion.h2>
            <motion.p
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="text-slate-400"
            >
                Our models adapt language and highlights based on the industry.
            </motion.p>
        </div>

        <div className="grid md:grid-cols-5 gap-12 items-center px-4 md:px-12">
            <div className="md:col-span-3 grid md:grid-cols-2 gap-8">
                <SectorCard
                    title="D2C Consumer Brand"
                    accent="text-brand-primary"
                    metrics={["Brand Overview", "Unit Economics", "Social Sentiment"]}
                    desc="Highlights CAC, LTV, and Instagram engagement growth."
                    index={0}
                />
                <SectorCard
                    title="Specialty Chemicals"
                    accent="text-brand-accent"
                    metrics={["Infrastructure", "Regulatory Compliance", "Supply Chain"]}
                    desc="Focuses on production capacity, patents, and safety ratings."
                    index={1}
                />
            </div>

            <div className="md:col-span-2">
                <GlobalNetwork3D />
            </div>
        </div>
    </section>
);

const GlobalNetwork3D = () => (
    <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        whileInView={{ opacity: 1, scale: 1 }}
        transition={{ duration: 1 }}
        className="relative h-[400px] flex items-center justify-center"
        style={{ perspective: "1000px" }}
    >
        <div className="relative w-full aspect-square max-w-[300px]">
            {[1, 2, 3, 4, 5].map((node, i) => (
                <motion.div
                    key={node}
                    animate={{
                        x: [Math.sin(i) * 100, Math.cos(i) * 120, Math.sin(i) * 100],
                        y: [Math.cos(i) * 100, Math.sin(i) * 120, Math.cos(i) * 100],
                        z: [i * 20, i * 40, i * 20],
                    }}
                    transition={{
                        duration: 10 + i * 2,
                        repeat: Infinity,
                        ease: "linear"
                    }}
                    className="absolute w-4 h-4 rounded-full bg-brand-primary shadow-[0_0_15px_rgba(14,165,233,0.8)]"
                    style={{ transformStyle: "preserve-3d" }}
                />
            ))}

            {/* Connecting Lines (Simulated with rotating elements) */}
            <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 30, repeat: Infinity, ease: "linear" }}
                className="absolute inset-0 border-[1px] border-brand-primary/10 rounded-full"
            />
            <motion.div
                animate={{ rotate: -360 }}
                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                className="absolute inset-0 border-[1px] border-brand-accent/10 rounded-full scale-125"
            />

            <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-20 h-20 bg-brand-primary/10 rounded-full blur-3xl animate-pulse" />
                <Database className="w-12 h-12 text-brand-primary" />
            </div>
        </div>
        <p className="absolute bottom-0 w-full text-center text-xs font-bold text-slate-500 tracking-widest uppercase">Global Dataset Network</p>
    </motion.div>
);

const SectorCard = ({ title, accent, metrics, desc, index }) => (
    <motion.div
        initial={{ opacity: 0, x: index === 0 ? -30 : 30 }}
        whileInView={{ opacity: 1, x: 0 }}
        viewport={{ once: true }}
        whileHover={{ scale: 1.02, y: -5 }}
        className="glass-card p-8 bg-brand-dark/50"
    >
        <h3 className={`text-2xl font-bold mb-4 ${accent}`}>{title}</h3>
        <p className="text-slate-300 mb-6 border-b border-white/10 pb-4">{desc}</p>
        <div className="space-y-3">
            {metrics.map((m, i) => (
                <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -10 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 + (i * 0.1) }}
                    className="flex items-center gap-3"
                >
                    <CheckCircle className="w-5 h-5 text-slate-500" />
                    <span className="text-slate-200">{m}</span>
                </motion.div>
            ))}
        </div>
    </motion.div>
);

const AnonymizationFeature = () => (
    <section className="section-padding grid md:grid-cols-5 gap-12 items-center">
        <motion.div
            initial={{ opacity: 0, x: -40 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.7 }}
            className="md:col-span-2"
        >
            <h2 className="text-3xl font-bold mb-6">Blind Anonymization Engine</h2>
            <p className="text-slate-400 text-lg mb-8">
                Protect sensitive client identity. Our engine automatically detects and replaces Proper Nouns, Locations, and Contact Info with neutralized placeholders.
            </p>
            <ul className="space-y-4">
                {[
                    { from: "Pfizer Inc", to: "Global Pharma Co" },
                    { from: "john@pfizer.com", to: "[Redacted Email]" }
                ].map((item, i) => (
                    <motion.li
                        key={i}
                        initial={{ opacity: 0, y: 10 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.5 + (i * 0.2) }}
                        className="flex items-center gap-3"
                    >
                        <Shield className="text-brand-accent w-6 h-6" />
                        <span className="text-slate-300">"{item.from}" → <span className="text-brand-accent font-medium">"{item.to}"</span></span>
                    </motion.li>
                ))}
            </ul>
        </motion.div>

        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.7 }}
            className="md:col-span-3 glass-card p-8 font-mono text-sm relative overflow-hidden"
        >
            <motion.div
                initial={{ x: "-100%" }}
                whileInView={{ x: "100%" }}
                transition={{ duration: 1.5, repeat: Infinity, repeatDelay: 3 }}
                className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-brand-primary to-brand-accent"
            />
            <div className="space-y-4">
                <div className="space-y-1">
                    <p className="text-slate-500">// Original Information</p>
                    <p className="text-red-300 line-through">CEO Tim Cook announces new campus in Cupertino.</p>
                </div>
                <div className="space-y-1">
                    <p className="text-slate-500">// Kelp AI Anonymized Output</p>
                    <motion.p
                        initial={{ opacity: 0 }}
                        whileInView={{ opacity: 1 }}
                        transition={{ delay: 1, duration: 1 }}
                        className="text-brand-accent border-l-2 border-brand-accent pl-4"
                    >
                        The CEO of Global Tech Co announces a new facility in the Western Region.
                    </motion.p>
                </div>
            </div>
        </motion.div>
    </section>
);

const VisualIntelligence = () => (
    <section className="section-padding text-center">
        <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            className="text-3xl md:text-5xl font-bold mb-12"
        >
            Visual Intelligence
        </motion.h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
                { name: "Pharma Lab", path: "/visuals/pharma.png" },
                { name: "Logistics", path: "/visuals/logistics.png" },
                { name: "SaaS Dash", path: "/visuals/dashboard.png" },
                { name: "Factory", path: "/visuals/factory.png" }
            ].map((img, i) => (
                <motion.div
                    key={i}
                    initial={{ opacity: 0, scale: 0.8 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    transition={{ delay: i * 0.1 }}
                    whileHover={{ scale: 1.05 }}
                    className="group relative aspect-square rounded-2xl overflow-hidden bg-slate-800 border border-white/5 shadow-2xl"
                >
                    <img
                        src={img.path}
                        alt={img.name}
                        className="absolute inset-0 w-full h-full object-cover opacity-40 group-hover:opacity-100 transition-all duration-700 scale-110 group-hover:scale-100"
                    />
                    <div className="absolute inset-0 bg-brand-primary/10 group-hover:bg-transparent transition-all duration-300" />
                    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                        <span className="font-bold text-white/50 group-hover:text-white group-hover:scale-110 transition-all duration-300 drop-shadow-2xl text-lg uppercase tracking-widest">{img.name}</span>
                    </div>
                </motion.div>
            ))}
        </div>
    </section>
);

const OutputPreview = () => (
    <section className="section-padding">
        <div className="grid md:grid-cols-2 gap-16 items-center">
            <div className="text-left">
                <motion.h2
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    className="text-3xl md:text-5xl font-bold mb-6"
                >
                    Your Deliverable
                </motion.h2>
                <motion.p
                    initial={{ opacity: 0 }}
                    whileInView={{ opacity: 1 }}
                    transition={{ delay: 0.3 }}
                    className="text-slate-400 text-lg mb-10"
                >
                    Get a fully editable, branded PowerPoint deck and a comprehensive citation guide in under 2 minutes. Our AI handles the layout, charts, and copy.
                </motion.p>
                <div className="space-y-4">
                    {["Perfectly Aligned Charts", "Custom Branding", "1-Click Download", "Audit Trails"].map((item, i) => (
                        <motion.div
                            key={item}
                            initial={{ opacity: 0, x: -20 }}
                            whileInView={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.4 + (i * 0.1) }}
                            className="flex items-center gap-3"
                        >
                            <div className="w-6 h-6 rounded-full bg-brand-primary/20 flex items-center justify-center">
                                <CheckCircle className="w-4 h-4 text-brand-primary" />
                            </div>
                            <span className="font-medium text-slate-300">{item}</span>
                        </motion.div>
                    ))}
                </div>
            </div>

            <HolographicDeliverable3D />
        </div>
    </section>
);

const HolographicDeliverable3D = () => (
    <motion.div
        initial={{ opacity: 0, x: 40 }}
        whileInView={{ opacity: 1, x: 0 }}
        transition={{ duration: 1 }}
        className="relative h-[500px] flex items-center justify-center"
        style={{ perspective: "1500px" }}
    >
        <div className="relative w-full max-w-[400px] aspect-[16/10]">
            {[
                { img: "/visuals/ppt_summary.png", z: 60 },
                { img: "/visuals/ppt_financials.png", z: 30 },
                { img: "/visuals/ppt_summary.png", z: 0 }
            ].map((item, i) => (
                <motion.div
                    key={i}
                    animate={{
                        rotateY: [-20, -10, -20],
                        rotateX: [15, 5, 15],
                        y: [i * -40, i * -40 - 20, i * -40],
                        z: item.z,
                    }}
                    transition={{
                        duration: 7,
                        repeat: Infinity,
                        ease: "easeInOut",
                        delay: i * 1
                    }}
                    className="absolute inset-0 rounded-xl shadow-2xl overflow-hidden border-2 border-brand-primary/10"
                    style={{ transformStyle: "preserve-3d", zIndex: 10 - i }}
                >
                    <img
                        src={item.img}
                        alt={`PPT Slide ${i + 1}`}
                        className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-gradient-to-tr from-brand-primary/5 to-transparent pointer-events-none" />
                </motion.div>
            ))}

            {/* Holographic Rays */}
            <motion.div
                animate={{
                    opacity: [0.1, 0.3, 0.1],
                    scale: [0.9, 1.1, 0.9],
                }}
                transition={{ duration: 5, repeat: Infinity }}
                className="absolute inset-0 bg-brand-primary/20 rounded-full blur-[100px] -z-10"
            />
        </div>
        <p className="absolute bottom-4 w-full text-center text-xs font-bold text-slate-500 tracking-widest uppercase">Holographic PPT Preview</p>
    </motion.div>
);

const TrustSection = () => (
    <section className="py-20 bg-slate-900 border-y border-white/5 text-center px-4">
        <motion.p
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            className="text-slate-500 uppercase tracking-widest text-sm font-semibold mb-8"
        >
            Trusted by Deal Teams at
        </motion.p>
        <div className="flex flex-wrap justify-center gap-12 items-center">
            {["Goldman", "Blackstone", "KKR", "Sequoia"].map((logo, i) => (
                <motion.span
                    key={logo}
                    initial={{ opacity: 0, filter: "grayscale(100%)" }}
                    whileInView={{ opacity: 0.5, filter: "grayscale(100%)" }}
                    whileHover={{ opacity: 1, filter: "grayscale(0%)", scale: 1.1 }}
                    transition={{ delay: i * 0.1 }}
                    className="text-2xl font-bold font-display text-white cursor-pointer"
                >
                    {logo}
                </motion.span>
            ))}
        </div>
    </section>
);

const CallToAction = () => (
    <section className="section-padding text-center py-32 relative overflow-hidden">
        <motion.div
            animate={{ scale: [1, 1.3, 1], opacity: [0.1, 0.2, 0.1] }}
            transition={{ duration: 10, repeat: Infinity }}
            className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-brand-primary/10 rounded-full blur-[120px] -z-10"
        />

        <motion.h2
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8 }}
            className="text-4xl md:text-6xl font-bold mb-8"
        >
            Ready to Accelerate <br /> Your Deal Flow?
        </motion.h2>
        <motion.p
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="text-xl text-slate-400 mb-12"
        >
            Generate your first Teaser in less than 2 minutes.
        </motion.p>
        <Link to="/signup">
            <motion.button
                whileHover={{ scale: 1.1, boxShadow: "0 0 30px rgba(14, 165, 233, 0.6)" }}
                whileTap={{ scale: 0.9 }}
                className="btn-primary text-lg px-10 py-4 shadow-brand-primary/40 shadow-2xl"
            >
                Generate Investment Teaser
            </motion.button>
        </Link>
    </section>
);

const Footer = () => (
    <footer className="py-12 border-t border-white/5 text-center text-slate-500 text-sm px-6">
        <div className="flex justify-center gap-8 mb-8">
            {["Privacy", "Terms", "Security"].map(item => (
                <motion.a key={item} href="#" whileHover={{ color: "#fff" }} className="transition-colors">{item}</motion.a>
            ))}
        </div>
        <motion.p
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
        >
            © 2026 Kelp AI. All rights reserved.
        </motion.p>
    </footer>
);

export default Landing;
