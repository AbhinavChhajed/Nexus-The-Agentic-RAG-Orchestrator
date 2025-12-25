import express, { Request, Response } from 'express';
import cors from 'cors';

const app = express();
const PORT = 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Define the shape of our expected request body
interface ChatRequest {
    message: string;
}

// Routes
app.get('/', (req: Request, res: Response) => {
    res.json({ status: "Backend is Running" });
});

app.post('/chat', (req: Request, res: Response) => {
    // We cast the body to our Interface to get autocomplete/safety
    const { message } = req.body as ChatRequest;
    
    console.log("Received:", message);

    // Mock Response
    const botReply = `I received your message: "${message}". (Backend Connected)`;

    res.json({ reply: botReply });
});

// Start Server
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});