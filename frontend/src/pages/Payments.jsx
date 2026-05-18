import { useState, useEffect } from 'react'
import { getAllPayments, createPayment, processPayment, refundPayment } from '../api/payments'
import { getAllOrders } from '../api/orders'

export default function Payments() {
    const [payments, setPayments] = useState([])
    const [orders, setOrders] = useState([])
    const [loading, setLoading] = useState(true)
    const [selectedOrder, setSelectedOrder] = useState('')
    const [method, setMethod] = useState('card')
    const [creating, setCreating] = useState(false)
    const [error, setError] = useState('')
    const selectedOrderData = orders.find(order => String(order.id) === String(selectedOrder))

    useEffect(() => {
        loadPayments()
        loadOrders()
    }, [])

    async function loadPayments() {
        try {
            setLoading(true)
            const data = await getAllPayments()
            setPayments(data.payments || [])
            setError('')
        } catch (err) {
            setError('Failed to load payments')
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    async function loadOrders() {
        try {
            const data = await getAllOrders()
            setOrders(data.orders || [])
        } catch (err) {
            console.error('Failed to load orders:', err)
        }
    }

    async function handleCreatePayment(e) {
        e.preventDefault()
        if (!selectedOrderData) {
            setError('Please select an order')
            return
        }

        try {
            setCreating(true)
            await createPayment(parseInt(selectedOrderData.id, 10), Number(selectedOrderData.total_price), 'KZT', method)
            setSelectedOrder('')
            setMethod('card')
            setError('')
            loadPayments()
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to create payment')
        } finally {
            setCreating(false)
        }
    }

    async function handleProcessPayment(paymentId) {
        try {
            await processPayment(paymentId)
            loadPayments()
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to process payment')
        }
    }

    async function handleRefund(paymentId) {
        try {
            await refundPayment(paymentId)
            loadPayments()
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to refund payment')
        }
    }

    const getStatusColor = (status) => {
        switch (status) {
            case 'completed':
                return 'green'
            case 'failed':
                return 'red'
            case 'pending':
                return 'orange'
            case 'refunded':
                return 'blue'
            default:
                return 'black'
        }
    }

    return (
        <div style={{ padding: '24px' }}>
            <h1>Payments</h1>

            {error && (
                <div style={{ background: '#ffebee', color: '#c62828', padding: '12px', borderRadius: '4px', marginBottom: '16px' }}>
                    {error}
                </div>
            )}

            {/* Create Payment Form */}
            <div style={{ background: '#f5f5f5', padding: '16px', borderRadius: '4px', marginBottom: '24px' }}>
                <h2>Create New Payment</h2>
                <form onSubmit={handleCreatePayment} style={{ display: 'grid', gap: '12px', maxWidth: '400px' }}>
                    <div>
                        <label style={{ display: 'block', marginBottom: '4px' }}>Order</label>
                        <select
                            value={selectedOrder}
                            onChange={(e) => setSelectedOrder(e.target.value)}
                            style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                        >
                            <option value="">Select an order...</option>
                            {orders.map(order => (
                                <option key={order.id} value={order.id}>
                                    Order #{order.id} - Product {order.product_id} (Qty: {order.quantity}) - {order.total_price} KZT
                                </option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label style={{ display: 'block', marginBottom: '4px' }}>Amount</label>
                        <div style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd', background: '#fafafa' }}>
                            {selectedOrderData ? `${selectedOrderData.total_price} KZT` : 'Select an order to see the amount'}
                        </div>
                    </div>

                    <div>
                        <label style={{ display: 'block', marginBottom: '4px' }}>Payment Method</label>
                        <select
                            value={method}
                            onChange={(e) => setMethod(e.target.value)}
                            style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                        >
                            <option value="card">Card</option>
                            <option value="bank_transfer">Bank Transfer</option>
                            <option value="wallet">Wallet</option>
                        </select>
                    </div>

                    <button
                        type="submit"
                        disabled={creating}
                        style={{
                            background: '#1976d2',
                            color: '#fff',
                            border: 'none',
                            padding: '10px 16px',
                            borderRadius: '4px',
                            cursor: creating ? 'not-allowed' : 'pointer',
                            opacity: creating ? 0.6 : 1
                        }}
                    >
                        {creating ? 'Creating...' : 'Create Payment'}
                    </button>
                </form>
            </div>

            {/* Payments List */}
            <div>
                <h2>Your Payments</h2>
                {loading ? (
                    <div>Loading...</div>
                ) : payments.length === 0 ? (
                    <div>No payments yet</div>
                ) : (
                    <div style={{ display: 'grid', gap: '12px' }}>
                        {payments.map(payment => (
                            <div key={payment.id} style={{
                                border: '1px solid #ddd',
                                padding: '16px',
                                borderRadius: '4px',
                                background: '#fff'
                            }}>
                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', marginBottom: '12px' }}>
                                    <div>
                                        <strong>Payment ID:</strong> {payment.id}
                                    </div>
                                    <div>
                                        <strong>Order ID:</strong> {payment.order_id}
                                    </div>
                                    <div>
                                        <strong>Amount:</strong> {payment.amount} {payment.currency}
                                    </div>
                                    <div>
                                        <strong>Method:</strong> {payment.method}
                                    </div>
                                    <div>
                                        <strong>Status:</strong> <span style={{ color: getStatusColor(payment.status) }}>
                                            {payment.status.toUpperCase()}
                                        </span>
                                    </div>
                                    <div>
                                        <strong>Transaction ID:</strong> {payment.transaction_id || 'N/A'}
                                    </div>
                                    <div>
                                        <strong>Created:</strong> {new Date(payment.created_at).toLocaleString()}
                                    </div>
                                    <div>
                                        <strong>Updated:</strong> {new Date(payment.updated_at).toLocaleString()}
                                    </div>
                                </div>

                                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                                    {payment.status === 'pending' && (
                                        <button
                                            onClick={() => handleProcessPayment(payment.id)}
                                            style={{
                                                background: '#4caf50',
                                                color: '#fff',
                                                border: 'none',
                                                padding: '8px 14px',
                                                borderRadius: '4px',
                                                cursor: 'pointer'
                                            }}
                                        >
                                            Process Payment
                                        </button>
                                    )}

                                    {payment.status === 'completed' && (
                                        <button
                                            onClick={() => handleRefund(payment.id)}
                                            style={{
                                                background: '#f44336',
                                                color: '#fff',
                                                border: 'none',
                                                padding: '8px 14px',
                                                borderRadius: '4px',
                                                cursor: 'pointer'
                                            }}
                                        >
                                            Request Refund
                                        </button>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}
