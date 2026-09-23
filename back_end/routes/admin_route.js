let express=require('express');
let router=express.Router();
router.get("/viewusers",(req,res)=>{
     res.send("viewusers route")
});
router.post("/addplants",(req,res)=>{
    res.send("addplants route")
});
router.put("/deleteusers/:id",async(req,res)=>{
    let result=await useSyncExternalStore.findByIdAndDelete(req.params.id)
    if (result){
        res.send("user deleted success");
    }else{
        res.send("no user found");
    }
});
router.get("/viewquestionary",(req,res)=>{
    res.send("view questionary route");
});

module.exports=router;
