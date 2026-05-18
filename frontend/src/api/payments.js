import { paymentClient } from "./client.js"

export async function createPayment(order_id, amount, currency = 'KZT', method = 'card') {
  const { data } = await paymentClient.post('/payments', { 
    order_id, 
    amount, 
    currency, 
    method 
  })
  return data
}

export async function getPayment(payment_id) {
  const { data } = await paymentClient.get(`/payments/${payment_id}`)
  return data
}

export async function getAllPayments() {
  const { data } = await paymentClient.get('/payments')
  return data
}

export async function processPayment(payment_id) {
  const { data } = await paymentClient.post(`/payments/${payment_id}/process`)
  return data
}

export async function refundPayment(payment_id) {
  const { data } = await paymentClient.post(`/payments/${payment_id}/refund`)
  return data
}
