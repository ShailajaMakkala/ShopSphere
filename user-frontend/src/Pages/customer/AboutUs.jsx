import React from "react";
import { FaShieldAlt, FaTruck, FaHeadset, FaLeaf, FaUsers, FaAward } from "react-icons/fa";

const stats = [
    { value: "2M+", label: "Happy Customers" },
    { value: "50K+", label: "Products Listed" },
    { value: "5K+", label: "Verified Vendors" },
    { value: "99%", label: "Satisfaction Rate" },
];

const values = [
    {
        icon: <FaShieldAlt size={28} />,
        title: "Trusted & Secure",
        desc: "Every transaction is protected with bank-grade security and end-to-end encryption.",
    },
    {
        icon: <FaTruck size={28} />,
        title: "Fast Delivery",
        desc: "Our logistics network ensures your order reaches you quickly and safely.",
    },
    {
        icon: <FaHeadset size={28} />,
        title: "24/7 Support",
        desc: "Our dedicated support team is always available to help you with any queries.",
    },
    {
        icon: <FaLeaf size={28} />,
        title: "Sustainable",
        desc: "We are committed to eco-friendly packaging and carbon-neutral delivery.",
    },
    {
        icon: <FaUsers size={28} />,
        title: "Community Driven",
        desc: "Built by the community, for the community — real reviews, real people.",
    },
    {
        icon: <FaAward size={28} />,
        title: "Award Winning",
        desc: "Recognized as India's best e-commerce platform for 3 consecutive years.",
    },
];

const teamData = [
    { name: "Vishnu", role: "", avatar: "VI", img: "/team/vishnu.jpg" },
    { name: "Sriram", role: "", avatar: "SR", img: "/team/sriram.png" },
    { name: "Mohana", role: "", avatar: "MO", img: "/team/mohana.png" },
    { name: "Balaji", role: "", avatar: "BA", img: "/team/balaji.png" },
    { name: "Subham", role: "", avatar: "SU", img: "/team/subham.png" },
    { name: "Sahithi", role: "", avatar: "SA", img: "/team/sahithi.png", align: "top" },
    { name: "Siri", role: "", avatar: "SI", img: "/team/siri.png" },
    { name: "Nandini", role: "", avatar: "NA", img: "/team/nandini.jpg" },
    { name: "Arjun", role: "", avatar: "AR", img: "/team/arjun.png" },
    { name: "Kushala", role: "", avatar: "KU", img: "/team/kushala.png" },
    { name: "Mahalaxmi", role: "", avatar: "MA", img: "/team/mahalaxmi.png" },
];

export default function AboutUs() {

    return (
        <div className="min-h-screen bg-gradient-to-br from-[#0f0720] via-[#1a0a35] to-[#0d0520] text-white">
            {/* Hero */}
            <section className="relative overflow-hidden py-24 px-4 text-center">
                <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-600/15 rounded-full blur-[120px]" />
                <div className="absolute bottom-0 right-1/4 w-80 h-80 bg-orange-500/10 rounded-full blur-[100px]" />
                <div className="relative z-10 max-w-3xl mx-auto">
                    <span className="inline-block px-4 py-1.5 rounded-full text-xs font-bold tracking-widest uppercase bg-orange-400/10 text-orange-400 border border-orange-400/20 mb-6">
                        Our Story
                    </span>
                    <h1 className="text-5xl md:text-6xl font-black mb-6 bg-gradient-to-r from-orange-400 via-purple-300 to-purple-500 bg-clip-text text-transparent leading-tight">
                        About ShopSphere
                    </h1>
                    <p className="text-purple-300/70 text-lg leading-relaxed">
                        We started with a simple belief — shopping should be joyful, affordable, and trustworthy.
                        ShopSphere was born in 2026 to bridge the gap between quality vendors and smart shoppers across India.
                    </p>
                </div>
            </section>

            {/* Stats */}
            <section className="py-16 px-4">
                <div className="max-w-5xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6">
                    {stats.map((s, i) => (
                        <div key={i} className="text-center p-6 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-sm hover:border-orange-400/30 transition-all duration-300">
                            <div className="text-4xl font-black bg-gradient-to-r from-orange-400 to-purple-400 bg-clip-text text-transparent mb-2">{s.value}</div>
                            <div className="text-purple-300/70 text-sm">{s.label}</div>
                        </div>
                    ))}
                </div>
            </section>

            {/* Our Values */}
            <section className="py-16 px-4">
                <div className="max-w-6xl mx-auto">
                    <h2 className="text-3xl font-black text-center mb-3 text-white">Our Core Values</h2>
                    <p className="text-center text-purple-300/60 text-sm mb-12">What we stand for, every single day.</p>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                        {values.map((v, i) => (
                            <div key={i} className="group p-7 rounded-2xl bg-white/5 border border-white/10 hover:border-purple-500/40 hover:bg-purple-500/5 transition-all duration-300">
                                <div className="text-orange-400 mb-4 group-hover:scale-110 transition-transform duration-300">{v.icon}</div>
                                <h3 className="text-white font-bold text-lg mb-2">{v.title}</h3>
                                <p className="text-purple-300/60 text-sm leading-relaxed">{v.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Mission */}
            <section className="py-16 px-4">
                <div className="max-w-4xl mx-auto text-center p-12 rounded-3xl bg-gradient-to-br from-purple-900/30 to-orange-900/10 border border-white/10">
                    <h2 className="text-3xl font-black mb-4 text-white">Our Mission</h2>
                    <p className="text-purple-300/70 text-lg leading-relaxed">
                        To empower every Indian household with access to quality products at fair prices, while creating meaningful livelihoods for thousands of vendors and delivery partners across the country.
                    </p>
                </div>
            </section>

            {/* Team */}
            <section className="py-16 px-4">
                <div className="max-w-7xl mx-auto">

                    <h2 className="text-3xl font-black text-center mb-3 text-white">Meet the Team</h2>
                    <p className="text-center text-purple-300/60 text-sm mb-12">The passionate people behind ShopSphere.</p>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-10">
                        {teamData.map((m, i) => (
                            <div key={i} className="flex flex-col items-center group">
                                <div className="relative w-full aspect-[4/5] rounded-[2.5rem] bg-white/5 border border-white/10 flex items-center justify-center text-white font-black text-5xl mx-auto mb-6 group-hover:scale-[1.02] transition-all duration-500 overflow-hidden shadow-2xl group-hover:border-orange-400/50">
                                    <div className="absolute inset-0 bg-gradient-to-t from-[#0f0720] via-transparent to-transparent opacity-60 z-10" />
                                    {m.img ? (
                                        <img
                                            src={m.img}
                                            alt={m.name}
                                            className={`w-full h-full object-cover group-hover:scale-110 transition-transform duration-700 ${m.align === 'top' ? 'object-top' : ''}`}
                                        />
                                    ) : (
                                        <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-orange-400/10 to-purple-600/10">
                                            <span className="bg-gradient-to-br from-orange-400 to-purple-400 bg-clip-text text-transparent">
                                                {m.avatar}
                                            </span>
                                        </div>
                                    )}
                                </div>
                                <div className="text-2xl font-bold text-white mb-1 group-hover:text-orange-400 transition-colors duration-300">{m.name}</div>
                                <div className="text-purple-300/40 text-xs font-black tracking-[0.2em] uppercase">{m.role || "Core Team"}</div>
                            </div>
                        ))}
                    </div>


                </div>
            </section>
        </div>
    );
}

