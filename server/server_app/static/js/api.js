function saveDataExams() {
    console.log('tuyet voi')
    let name = document.getElementById('name').value;
    let date = document.getElementById('date').value;
    let symptom = document.getElementById('symptom').value;
    let disease = document.getElementById('disease').value;
    let medicineName = document.getElementById('medicineName').value;
    let quantity = document.getElementById('quantity').value;
    let unit = document.getElementById('unit').value;
    let instruction = document.getElementById('instruction').value;

    let examData = {
        'name': name,
        'date': date,
        'symptom': symptom,
        'disease': disease,
        'medicineName': medicineName,
        'quantity': quantity,
        'unit': unit,
        'instruction': instruction
    };

    fetch('/api/save_exam_data', {
        method: 'post',
        body: JSON.stringify(examData),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(res => { 
        console.info(res)    
        return res.json()          
    }).then(data => {
        console.info(data)
    }).catch(err => {
        console.error(err)
    })
};

window.addEventListener('load', function() {
    fetch('/api/get_exam_data')
    .then(response => response.json())
    .then(data => {
        document.getElementById('name').value = data.name || '';
        document.getElementById('date').value = data.date || '';
        document.getElementById('symptom').value = data.symptom || '';
        document.getElementById('disease').value = data.disease || '';
        document.getElementById('medicineName').value = data.medicineName || '';
        document.getElementById('quantity').value = data.quantity || '';
        document.getElementById('unit').value = data.unit || '';
        document.getElementById('instruction').value = data.instruction || '';
    }).catch(err => {
        console.error(err)
    });
});

function pay(phieuKhamId) {
    if(confirm('Bạn chắc chắn có muốn thanh toán không?') == true) {
        fetch('/api/pay', {
            method: 'post',
            body: JSON.stringify({
                'phieuKhamId':phieuKhamId
            }),
            headers:{
                'Content-Type':'application/json'
            }
        }).then(res => res.json()).then(data => {
            if(data.code === 200)
                location.reload()
        }).catch(err => console.error(err))
    }
}

// function addToMedicine(id,tenThuoc,donGia){

//     fetch('/api/add-medicine',{
//         method: 'post',
//         body: JSON.stringify({
//             'id':id,
//             'tenThuoc':tenThuoc,
//             'donGia':donGia
//         }),
//         headers:{
//             'Content-Type':'application/json'
//         }
//     }).then(function (response ){
//         return response.json()
//     }).then(function (data){
//         let counter = document.getElementById('count_medicine')
//         counter.innerText =data.total_quantity
//         number=data.total_quantity
//     }).catch(function (err){
//         console.error(err)
//     })
// }