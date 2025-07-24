import { useState } from 'react';
import { toast } from 'react-hot-toast';
import { submitTransaction } from '../services/api';

export default function SubmitTransaction() {
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        amount: '',
        description: '',
        recipient: '',
        type: 'payment'
    });

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            await submitTransaction(formData);
            toast.success('Transaction submitted successfully');
            setFormData({
                amount: '',
                description: '',
                recipient: '',
                type: 'payment'
            });
        } catch (err) {
            toast.error(err.response?.data?.message || 'Failed to submit transaction');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-md mx-auto">
            <h1 className="text-2xl font-bold mb-4">Submit Transaction</h1>
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block mb-1">Amount</label>
                    <input
                        type="number"
                        step="0.01"
                        className="w-full border p-2 rounded"
                        value={formData.amount}
                        onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                        required
                    />
                </div>

                <div>
                    <label className="block mb-1">Recipient</label>
                    <input
                        type="text"
                        className="w-full border p-2 rounded"
                        value={formData.recipient}
                        onChange={(e) => setFormData({ ...formData, recipient: e.target.value })}
                        required
                    />
                </div>

                <div>
                    <label className="block mb-1">Description</label>
                    <textarea
                        className="w-full border p-2 rounded"
                        value={formData.description}
                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                        required
                    />
                </div>

                <div>
                    <label className="block mb-1">Type</label>
                    <select
                        className="w-full border p-2 rounded"
                        value={formData.type}
                        onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                    >
                        <option value="payment">Payment</option>
                        <option value="transfer">Transfer</option>
                        <option value="deposit">Deposit</option>
                    </select>
                </div>

                <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600 disabled:opacity-50"
                >
                    {loading ? 'Submitting...' : 'Submit Transaction'}
                </button>
            </form>
        </div>
    );
}
