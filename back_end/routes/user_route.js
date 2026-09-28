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
router.patch("/updateprofile/:id",async(req,res)=>{
    let data=req.body;
    if(data.password){
        data.password=await bcrypt.hash(data.password,10);
        }
        let result=await users.findByIdAndUpdate(req.params.id,data,{new:true});
        res.send(result);
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