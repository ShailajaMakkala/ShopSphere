import React from 'react';
import { motion } from 'framer-motion';
import { RefreshCcw, ShieldCheck, Clock, Truck } from 'lucide-react';
import { Link } from 'react-router-dom';

const Returns = () => {
    const steps = [
        {
            icon: Clock,
            title: "Initiate Request",
            description: "Go to your orders and click 'Return Item' within 30 days of delivery."
        },
        {
            icon: Truck,
            title: "Pack Item",
            description: "Place items in original packaging with all tags and accessories."
        },
        {
            icon: RefreshCcw,
            title: "Pick Up",
            description: "Our delivery agent will pick up the item from your doorstep."
        },
        {
            icon: ShieldCheck,
            title: "Get Refund",
            description: "Once inspected, your refund will be processed within 5-7 business days."
        }
    ];

    return (
        <div className="min-h-screen bg-white dark:bg-gray-900 py-16 px-4">
            <div className="max-w-7xl mx-auto">
                <div className="text-center mb-16">
                    <h1 className="text-4xl font-black text-gray-900 dark:text-white mb-4">Returns & Refunds</h1>
                    <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto text-lg">
                        Shopping with confidence is our priority. If you're not satisfied, we've made the return process as simple as possible.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-20">
                    {steps.map((step, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1 }}
                            className="bg-gray-50 dark:bg-gray-800 p-8 rounded-3xl text-center relative"
                        >
                            <div className="inline-flex items-center justify-center p-4 bg-blue-100 dark:bg-blue-900/30 rounded-2xl mb-6">
                                <step.icon className="w-8 h-8 text-blue-600 dark:text-blue-400" />
                            </div>
                            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">{step.title}</h3>
                            <p className="text-gray-600 dark:text-gray-400">{step.description}</p>

                            {index < steps.length - 1 && (
                                <div className="hidden lg:block absolute top-1/2 -right-4 transform -translate-y-1/2 z-10">
                                    <div className="w-8 h-0.5 bg-gray-200 dark:bg-gray-700"></div>
                                </div>
                            )}
                        </motion.div>
                    ))}
                </div>

                <div className="bg-blue-600 rounded-[3rem] p-12 text-white flex flex-col md:flex-row items-center justify-between shadow-2xl shadow-blue-500/20">
                    <div className="mb-8 md:mb-0 md:mr-8 text-center md:text-left">
                        <h2 className="text-3xl font-bold mb-4">Need help with a return?</h2>
                        <p className="text-blue-100 text-lg">Contact our 24/7 support team for immediate assistance with any return or refund related queries.</p>
                    </div>
                    <Link to="/contact">
                        <button className="bg-white text-blue-600 px-10 py-4 rounded-2xl font-black text-lg hover:bg-blue-50 transition-colors whitespace-nowrap">
                            Go to Support
                        </button>
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default Returns;
