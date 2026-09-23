let express=require('express');
let router=express.Router();
router.post("/addusers",(req,res)=>{
    res.send("add users the route")
});
router.post("/login",(req,res)=>{
     res.send("login the route")
});
router.put("/updateresponse",(req,res)=>{
    res.send("update response  route");
});
router.put("/updateprofile",(req,res)=>{
    res.send("update profile route");
});
router.post("/addquestionary",(req,res)=>{
    res.send("add questionary route");
});
router.get("/viewquestionary",(req,res)=>{
    res.send("view questionary route");
});
router.get("/viewplants",(req,res)=>{
    res.send("view plants route");
});
module.exports=router;