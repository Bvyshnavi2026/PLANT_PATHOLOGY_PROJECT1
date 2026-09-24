let express=require('express');
let router=express.Router();
router.post("/addusers",(req,res)=>{
    res.send("add users the route")
});
router.post("/login",async(req,res)=>{
    let result=await users.findOne({email:req.body.email})
    // result.password=undefined;
    if(result)
        {
        let matchpass=await bcrypt.compare(req.body.password,result.password);
        if(matchpass){
            res.send("Login Successfull");
        }else{
            res.send("Login failed");
        }
    }else{
            res.send("user not found");
        }
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