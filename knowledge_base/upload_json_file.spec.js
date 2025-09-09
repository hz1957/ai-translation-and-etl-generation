import { test, expect } from '@playwright/test';
test.use({ headless: false });
test('观远数据导出操作', async ({ page }) => {
        // 登录
    await page.goto('https://bipoc.pharmaronclinical.com/auth/index');
    await page.waitForLoadState('networkidle');

    // 输入凭据
    await page.getByRole('textbox', { name: 'Account' }).click();
    await page.getByRole('textbox', { name: 'Account' }).fill('Tianjian');
    await page.getByRole('textbox', { name: 'Password' }).fill('ABCabc123');
    await page.getByText('Login').click();

    // 等待登录完成
    await page.waitForLoadState('networkidle');

    // 步骤 2-3: 导航和文件上传
    await page.getByRole('tab', { name: '数据准备' }).click();
    await page.getByText('智能ETL').click();
    await page.getByRole('button', { name: '新建ETL' }).click();
    await page.getByTestId('data-flows-edit').locator('div').filter({ hasText: 'New Transform所在目录:根目录撤销恢复更新设置取消保存' }).locator('i').nth(4).click();
    await page.getByRole('menuitem', { name: ' 导入' }).locator('div').nth(1).click();
    await page.getByText('点击上传文件').click();

    // 关键步骤: 文件上传和验证
    const fileInput = page.getByLabel('导入').locator('input[type="file"]');
    
    // 从环境变量获取JSON数据并转换为buffer
    const jsonData = process.env.JSON_DATA || '{}';
    const buffer = Buffer.from(jsonData, 'utf-8');
    
    await fileInput.setInputFiles({
        name: 'agent-upload.json',
        mimeType: 'application/json',
        buffer
    });

    // 等待上传处理
    await page.waitForTimeout(3000);


    // 检查上传错误
    const errorCount = await page.locator('text=文件格式不正确').count();
    if (errorCount > 0) {
        console.log(`文件上传错误，共 ${errorCount} 条`);
        return; // 停止执行
    }

    // 点击下一步和确定
    await page.getByRole('button', { name: '下一步' }).click();
    await page.getByRole('button', { name: '确定' }).click();

    // 等待 JS 执行错误提示
    const jsErrorCount = await page.locator('text=JsResultException(errors:List)').count();
    if (jsErrorCount > 0) {
        console.log(`出现 JS 执行错误，共 ${jsErrorCount} 条`);
        return; // 停止执行
    }

    console.log('文件上传并处理成功');

});