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
    thisUserAddedFrom: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User', // Assuming the reference is to another user; change 'User' to the correct model name as necessary
      default: null, // You might want to set this to null or not include it if you don't want a default value
    },
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
      const { name, mobileNumber , thisUserAddedFrom } = req.body;
      const newUser = new User({
        name,
        mobileNumber,
        thisUserAddedFrom
      })
  await newUser.save();
  res.status(201).json({ message: 'User added successfully', user: newUser });
    } catch (error) {
      // Handle any errors during the process
      res.status(500).json({ message: 'Error during login', error });
    }
  });

  app.post('/delete-user/:userId', async (req, res) => {
    try {
      const { userId } = req.params;
      console.log("eeee",userId)
      if (userId) {
        const deletedUser = await User.findByIdAndDelete(userId, { new: true });
        
        if (!deletedUser) {
          return res.status(404).json({ message: 'User not found' });
        }
        
        res.status(200).json({ message: 'User deleted successfully', user: deletedUser });
      } else {
        res.status(400).json({ message: 'No file uploaded' });
      }
    } catch (error) {
      res.status(500).json({ message: 'Error deleting user', error: error.message });
    }
  });

  app.post('/updateProfilePic/:userId', upload.single('profilePic'), async (req, res) => {
    try {
      const { userId } = req.params;
  
      if (req.file) {
        const profilePicPath = req.file.path;
         console.log("profilePicPath:::",profilePicPath)
        const updatedUser = await User.findByIdAndUpdate(userId, { profilePic: profilePicPath }, { new: true });
        
        if (!updatedUser) {
          return res.status(404).json({ message: 'User not found' });
        }
        
        res.status(200).json({ message: 'Profile picture updated successfully', user: updatedUser });
      } else {
        res.status(400).json({ message: 'No file uploaded' });
      }
    } catch (error) {
      res.status(500).json({ message: 'Error updating profile', error: error.message });
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

const userSockets = {};

io.on('connection', (socket) => {
  console.log('New client connected');

  socket.on('joinChat', ({ userId, contactId }) => {
      const roomId = [userId, contactId].sort().join("_");
      socket.join(roomId);
  });

  socket.on('sendMessage', async ({ message, to, sender }) => {
      const roomId = [sender, to].sort().join("_");
      const newMessage = new Message({ sender, receiver: to, message });
      await newMessage.save();

      // Emit to users in the same room
      io.to(roomId).emit('message', newMessage);
  });

  socket.emit('myId', socket.id);

  socket.on('callUser', ({ userToCall, signalData, from, name }) => {
    io.to(userToCall).emit('callReceived', { signal: signalData, from, name });
    console.log('callReceived:', from, name);
  });

  socket.on('acceptCall', (data) => {
    io.to(data.to).emit('callAccepted', data.signal);
    console.log('callAccepted:', data);
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
