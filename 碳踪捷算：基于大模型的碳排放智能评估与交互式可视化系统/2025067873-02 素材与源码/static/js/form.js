// static/js/form.js
// 通过这些调整，<label class="prefix">行</label> 和 <label class="prefix">食</label> 将会有一个固定且一致的宽度，等于一个中文字符的宽度，从而保持网页的整齐和美观。
function addField() {
    const div = document.createElement('div');
    div.className = 'input-group';
    div.innerHTML = `
        <select name="category[]" required>
            <option value="短途出行">🚗 短途出行</option>
            <option value="中途出行">🚌 中途出行</option>
            <option value="长途出行">✈️ 长途出行</option>
            <option value="主食">🍚 主食</option>
            <option value="蔬果">🥦 蔬果</option>
            <option value="肉蛋奶">🥩 肉蛋奶</option>
            <option value="棉麻类">👕 棉麻类</option>
            <option value="化纤类">👔 化纤类</option>
            <option value="混纺类">👖 混纺类</option>
        </select>
        <input type="number" step="0.1" name="value[]" placeholder="" required>
    `;
    document.getElementById('inputs').appendChild(div);
}
