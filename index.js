const express = require('express');
const http = require('http');
const mongoose = require('mongoose');
const socketIo = require('socket.io');
const cors = require('cors');
const multer = require('multer');
const helmet = require('helmet');
const path = require('path');
const { fileUpload } = require('./utils/fileUploadMinio');
require("dotenv").config()
const app = express();
app.use(cors());
app.use(express.json());
app.use(helmet());

app.use(express.static(path.join(__dirname, 'build')));

const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"],
  },
});

// MongoDB connection
// MongoDB connection
mongoose.connect('mongodb+srv://akshayghugare0:root@cluster0.rwu4clq.mongodb.net/chatmyapp?retryWrites=true&w=majority', { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => console.log('MongoDB connected'))
  .catch(err => console.log(err));


  const userSchema = new mongoose.Schema({
    name: String,
    mobileNumber: String,
    isLogin: {
      type: Boolean,
      default: false,
    },
    profilePic: {
      type:String,
      default:''
    }, // Stores the path to the image
    timestamp: {
      type: Date,
      default: Date.now,
    },
  });

const User = mongoose.model('User', userSchema);

const messageSchema = new mongoose.Schema({
  sender: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
  receiver: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
  message: String,
  timestamp: { type: Date, default: Date.now },
});

const Message = mongoose.model('Message', messageSchema);

// Multer setup for file uploads
const storage = multer.diskStorage({
  destination: function(req, file, cb) {
    cb(null, 'uploads/') // Ensure this directory exists
  },
  filename: function(req, file, cb) {
    cb(null, file.fieldname + '-' + Date.now() + '.' + file.originalname.split('.').pop())
  }
});

const upload = multer({ storage: storage });

// Serve static files from uploads directory
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

//login user
app.post('/login', async (req, res) => {
    try {
      const { name, mobileNumber } = req.body;
      const user = await User.findOneAndUpdate(
        {name, mobileNumber }, 
        { $set: { isLogin: true } }, 
        { new: true } 
      );
  
      if (user) {
        // If a user is found, login is successful
        res.status(200).json({ message: 'Login successful', user });
      } else {
        // If no user is found, login fails
        res.status(404).json({ message: 'User not found' });
      }
    } catch (error) {
      // Handle any errors during the process
      res.status(500).json({ message: 'Error during login', error });
    }
  });
 
  app.post('/logout', async (req, res) => {
    try {
      const { name, mobileNumber } = req.body;
  
      // Attempt to find a user with the given name and mobile number
      // const user = await User.findOne({ name, mobileNumber });
      const user = await User.findOneAndUpdate(
        {name, mobileNumber }, // condition to find the user by mobile number
        { $set: { isLogin: false } }, // update operation to set isLogin to true
        { new: true } // options to return the updated document
      );
  
      if (user) {
        // If a user is found, login is successful
        res.status(200).json({ message: 'Logout successful', user });
      } else {
        // If no user is found, login fails
        res.status(404).json({ message: 'User not found' });
      }
    } catch (error) {
      // Handle any errors during the process
      res.status(500).json({ message: 'Error during login', error });
    }
  });

  app.post('/signup', async (req, res) => {
    try {
      const { name, mobileNumber } = req.body;
      const newUser = new User({
        name,
        mobileNumber,
      })
  await newUser.save();
  res.status(201).json({ message: 'User added successfully', user: newUser });
    } catch (error) {
      // Handle any errors during the process
      res.status(500).json({ message: 'Error during login', error });
    }
  });

  app.post('/addUser', async (req, res) => {
    try {
      const { name, mobileNumber } = req.body;
      const newUser = new User({
        name,
        mobileNumber,
      })
  await newUser.save();
  res.status(201).json({ message: 'User added successfully', user: newUser });
    } catch (error) {
      // Handle any errors during the process
      res.status(500).json({ message: 'Error during login', error });
    }
  });



app.post('/updateProfilePic/:userId', upload.single('profilePic'), async (req, res) => {
  try {
    const { userId } = req.params;
    

    if (req.file) {
      const file = req.file;
      const objectName = `profilepic/${file.originalname}`;
      const uploadResult = await fileUpload(objectName, file.path);
      let profilePic;
      if (uploadResult) {
        profilePic = uploadResult;
      }
      const updatedUser = await User.findByIdAndUpdate(userId, profilePic, { new: true });
    if (!updatedUser) {
      return res.status(404).json({ message: 'User not found' });
    }
    res.status(200).json({ message: 'Profile updated successfully', user: updatedUser });
    }
  } catch (error) {
    res.status(500).json({ message: 'Error updating profile', error });
  }
});

// Fetch all users
app.get('/getAllUsers', async (req, res) => {
  try {
    const users = await User.find({});
    res.status(200).json(users);
  } catch (error) {
    res.status(500).json({ message: 'Error fetching users', error });
  }
});

// Fetch messages between two users
app.get('/getMessages/:userId/:contactId', async (req, res) => {
  try {
    const { userId, contactId } = req.params;
    const messages = await Message.find({
      $or: [
        { sender: userId, receiver: contactId },
        { sender: contactId, receiver: userId },
      ],
    }).sort('timestamp');
    res.status(200).json(messages);
  } catch (error) {
    res.status(500).json({ message: 'Error fetching messages', error });
  }
});

// Socket.IO for real-time communication
io.on('connection', (socket) => {
  console.log('New client connected');

  socket.on('sendMessage', async ({ message, to, sender }) => {
    if (!message.trim() || !to || !sender) {
      console.error('Invalid message data:', { message, to, sender });
      return;
    }

    try {
      const newMessage = new Message({ sender, receiver: to, message });
      await newMessage.save();

      socket.join([to, sender]); // Join both sender and receiver to their rooms
      io.to(to).emit('message', newMessage);
      io.to(sender).emit('message', newMessage);
    } catch (error) {
      console.error('Error sending message:', error);
    }
  });

  socket.on('disconnect', () => {
    console.log('Client disconnected');
  });
});
app.get('/test', (req, res) => {
  res.send("Hello from API");
});

app.get('/*', (req, res) => {
    res.sendFile(path.join(__dirname, 'build', 'index.html'));
  });


const PORT = process.env.PORT || 4000;
server.listen(PORT, () => console.log(`Server running on port ${PORT}`));
