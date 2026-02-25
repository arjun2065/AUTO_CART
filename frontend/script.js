

document.addEventListener("DOMContentLoaded",() => {
  document.addEventListener("backbutton", (event) => {event.preventDefault();
if(window.location.pathname.endsWith(cart.html)) {
  window.location.href = "index.html";
}   else{
  navigator.app.exitApp();
}
})
})

console.log("JS loaded");


const cartid = localStorage.getItem("cartID");


console.log("JS loaded");
let cartentries=JSON.parse((localStorage.getItem("cartentries")))||[];
document.addEventListener("DOMContentLoaded",()=>{
        const carte = document.getElementById("cart");
       
        const cart=JSON.parse(localStorage.getItem("cartentries"))||[]
        
        
       

        
        carte.innerHTML="";
        cart.forEach(product=>{carte.insertAdjacentHTML("beforeend", `
          <div class="cartitem">
            <div class="left">
              <strong>${product.item}</strong><br>
              Barcode: ${product.barcode}<br>
              Weight: ${product.weight}
            </div>

            <div class="right">
              <div>Price: ₹${product.price}</div>
              <div>Discount: ₹${product.discount}</div>
              <div>quantity: ${product.quantity}</div>
              <div><strong>Total: ₹${product.price - product.discount}</strong></div>
            </div>
          </div>
        `
        
    )});
    cart.forEach(product=>{
        totalprice=cart.reduce((sum,product)=>sum+(product.price-product.discount),0)
        document.getElementById("carttotal").textContent=`₹${totalprice}`})
        localStorage.setItem("totalamount",totalprice);
    })



const socket=new  WebSocket("wss://auto-cart.onrender.com/ws")
socket.onopen = () => {
  console.log("connected");

  socket.send(JSON.stringify({
    "connection":"sub",
    "cartID":cartid
  }))


socket.onmessage=(event) =>{
  const data=JSON.parse(event.data)
  console.log(event.data)
  if (!data.barcode) {
   
    return;
  
  }
  fetch(`https://auto-cart.onrender.com/get_product/${data.barcode}`)
    .then(res => res.json())
    .then(product => {
      
      console.log("Data from server:", product);
      const carte = JSON.parse(localStorage.getItem("cartentries"))||[];
      const userid=localStorage.getItem("user")
      
      let cartentries=JSON.parse((localStorage.getItem("cartentries")))||[];

      const exitem=cartentries.find(x=>x.barcode===product.barcode);
        console.log(exitem)
        
        if(exitem){
          exitem.quantity+=1;
          
          
          
        }
        else{
          cartentries.push({
            "barcode":product.barcode,
            "discount":product.discount,
            "item":product.item,
            "price":product.price,
            "weight":product.weight,
            "quantity":1
          });
        }
        
      
      
      
      localStorage.setItem("cartentries",JSON.stringify(cartentries))
      totalprice=cartentries.reduce((sum,product)=>sum+((product.price-product.discount)*product.quantity),0)
      document.getElementById("carttotal").textContent=`₹${totalprice}`;
      localStorage.setItem("totalamount",totalprice);
      fetch(`https://auto-cart.onrender.com/add_cart`,{
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body:JSON.stringify({
                "sessionid":localStorage.getItem("sessionid"),
                "userid":userid,
                "barcode":product.barcode
            })
            
            })
            .then(res => res.json())
            .then(data =>{
              console.log(data)
            })

      
      const cart = document.getElementById("cart");
      const carten = JSON.parse(localStorage.getItem("cartentries"))||[];
      

      

      cart.innerHTML="";
      carten.forEach(product=>{cart.insertAdjacentHTML("beforeend", `
        <div class="cartitem">
          <div class="left">
            <strong>${product.item}</strong><br>
            Barcode: ${product.barcode}<br>
            Weight: ${product.weight}
          </div>

          <div class="right">
            <div>Price: ₹${product.price}</div>
            <div>Discount: ₹${product.discount}</div>
            <div>quantity: ${product.quantity}</div>
            <div><strong>Total: ₹${product.price - product.discount}</strong></div>
          </div>
        </div>
      `)});
    
        
    })
    
    .catch(err => {
      console.error("Fetch failed:", err);
    });
};
}

