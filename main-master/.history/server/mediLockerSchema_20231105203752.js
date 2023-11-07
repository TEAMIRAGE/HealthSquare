const mongoose = require("mongoose");

const MediLockerSchema = mongoose.Schema({
  ReportName: {
    type: String,
    required: true,
  },
  date:{
    type: Date,
    required:true,
  }
  Imagename: {
    type: String,
    required: true,
  },

  UserId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: "userDetails",
  },
});

const MediLockerDB = mongoose.model("MediLockerCollection", MediLockerSchema);

module.exports = MediLockerDB;
