import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, Search, HelpCircle } from 'lucide-react';

const FAQItem = ({ question, answer, isOpen, onClick }) => (
    <div className="border-b border-gray-200 dark:border-gray-700">
        <button
            onClick={onClick}
            className="w-full py-6 flex items-center justify-between text-left focus:outline-none"
        >
            <span className="text-lg font-semibold text-gray-900 dark:text-white pr-8">
                {question}
            </span>
            <motion.div
                animate={{ rotate: isOpen ? 180 : 0 }}
                transition={{ duration: 0.2 }}
            >
                <ChevronDown className="w-5 h-5 text-gray-500" />
            </motion.div>
        </button>
        <AnimatePresence>
            {isOpen && (
                <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3, ease: 'easeInOut' }}
                    className="overflow-hidden"
                >
                    <div className="pb-6 text-gray-600 dark:text-gray-400 leading-relaxed">
                        {answer}
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    </div>
);

const FAQ = () => {
    const [openIndex, setOpenIndex] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');

    const faqs = [
        {
            question: "How do I track my order?",
            answer: "Once your order is shipped, you will receive a tracking ID via email. You can enter this ID in the 'Order Tracking' section of your profile to see real-time updates."
        },
        {
            question: "What is your return policy?",
            answer: "We offer a 30-day return policy for most items. The product must be in its original packaging and condition. Some items like perishables and personalized goods are not returnable."
        },
        {
            question: "How can I contact a seller?",
            answer: "You can find seller information on the product detail page. We also provide a messaging system to communicate directly with vendors regarding specific items."
        },
        {
            question: "Is my payment secure?",
            answer: "Yes, we use industry-standard encryption and secure payment gateways. We never store your full credit card details on our servers."
        },
        {
            question: "How do I become a vendor?",
            answer: "Click on 'Sell on ShopSphere' in the header. You'll need to provide business registration details and valid ID for verification."
        }
    ];

    const filteredFaqs = faqs.filter(faq =>
        faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
        faq.answer.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-3xl mx-auto">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center mb-12"
                >
                    <div className="inline-flex items-center justify-center p-3 bg-blue-100 dark:bg-blue-900/30 rounded-2xl mb-4">
                        <HelpCircle className="w-8 h-8 text-blue-600 dark:text-blue-400" />
                    </div>
                    <h1 className="text-4xl font-extrabold text-gray-900 dark:text-white sm:text-5xl mb-4">
                        Frequently Asked Questions
                    </h1>
                    <p className="text-xl text-gray-600 dark:text-gray-400">
                        Everything you need to know about shopping with us.
                    </p>
                </motion.div>

                <div className="relative mb-12">
                    <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                        type="text"
                        placeholder="Search for answers..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full pl-12 pr-4 py-4 rounded-2xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 transition-all shadow-sm"
                    />
                </div>

                <motion.div
                    layout
                    className="bg-white dark:bg-gray-800 rounded-3xl shadow-xl overflow-hidden border border-gray-100 dark:border-gray-700 px-8"
                >
                    {filteredFaqs.length > 0 ? (
                        filteredFaqs.map((faq, index) => (
                            <FAQItem
                                key={index}
                                question={faq.question}
                                answer={faq.answer}
                                isOpen={openIndex === index}
                                onClick={() => setOpenIndex(openIndex === index ? null : index)}
                            />
                        ))
                    ) : (
                        <div className="py-12 text-center text-gray-500">
                            No matching FAQs found. Please try a different search term.
                        </div>
                    )}
                </motion.div>
            </div>
        </div>
    );
};

export default FAQ;
