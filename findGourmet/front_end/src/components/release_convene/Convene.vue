<template>
    <div>
        <!-- 面包屑 -->
        <el-breadcrumb separator-class="el-icon-arrow-right">
            <el-breadcrumb-item :to="{ path: '/welcome' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>寻找美食</el-breadcrumb-item>
            <el-breadcrumb-item>发布寻味道</el-breadcrumb-item>
        </el-breadcrumb>
        <!-- 发布寻味道主体 -->
        <h2>填写相关信息</h2>
        <el-form :model="callForm" :rules="callRules" ref="callFormRef" label-width="120px">
            <el-form-item label="寻味道类型" prop="typeName">
                <el-select v-model="callForm.typeId" placeholder="请选择寻味道类型" @change="showMessage($event)">
                    <el-option
                        v-for="item in callOption"
                        :key="item.TypeId"
                        :label="item.TypeName"
                        :value="item.TypeId"
                    >
                    </el-option>
                </el-select>
            </el-form-item>
            <el-form-item label="寻味道名称" prop="name">
                <el-input v-model="callForm.name"></el-input>
            </el-form-item>
            <el-form-item label="寻味道描述" prop="description">
                <el-input type="textarea" v-model="callForm.description"></el-input>
            </el-form-item>
            <el-form-item label="寻找人数" prop="peopleCount">
                <el-input v-model="callForm.peopleCount"></el-input>
            </el-form-item>
            <el-form-item label="寻找结束日期" required>
                <el-col :span="11">
                <el-form-item prop="endTime">
                    <el-date-picker type="datetime" placeholder="选择日期" v-model="callForm.endTime" value-format="yyyy-MM-dd HH:mm:ss" :picker-options="expireTimeOption" style="width: 100%;"></el-date-picker>
                </el-form-item>
                </el-col>
            </el-form-item>
            <!-- 提交按钮 -->
            <el-form-item>
                <el-button type="primary" @click="submit()">发布</el-button>
                <el-button type="info" @click="reset()">重置</el-button>
            </el-form-item>
        </el-form>
    </div>
</template>

<script>
export default {
    data() {
        return {
            callOption: [], // 寻味道类型列表
            callForm: {
                userId: this.$store.state.user.id,
                typeName: '',
                name: '',
                description: '',
                endTime: '',
                peopleCount: 3,
                typeId: ''
            },
            expireTimeOption: {
                disabledDate(date) {
                    return date.getTime() <= Date.now();
                }
            },
            callRules: {
                typeName: [
                    { required: true, message: '请选择寻味道类型', trigger: 'blur' },
                ],
                name: [
                    { required: true, message: '请输入寻味道名称', trigger: 'blur' },
                ],
                description: [
                    { required: true, message: '请输入寻味道描述', trigger: 'blur' },
                ],
                peopleCount: [
                    { validator: this.check_cnt, trigger: 'blur' },
                ],
                endTime: [
                    { required: true, message: '请选择寻味道结束时间', trigger: 'blur'}
                ]
            }
        }
    },
    created() {
        var that = this
        this.$http.get("/findG/getType", {
                headers: {
                    'Authorization': "Bearer "+ window.sessionStorage.getItem('token') 
                }
        })
        .then(function(response) {
            if (response.status == 200) {
                that.callOption = response.data
            } else {
                that.$message({showClose: true, message: response.message, type: 'warning'})
            }
        })
        .catch(function(error) {
            console.log(error)
            that.$message({showClose: true, message: "请求错误", type: 'error'})
        })
    },
    methods: {
        // 检查寻找人数
        check_cnt(rule, value, callback) {
            if (String(value).trim() == '') {
                return callback(new Error('请输入寻找人数'))
            } else if (Number(value) <= 0 || Number(value) >=101) {
                return callback(new Error('寻找人数必须在1~100内'))
            } else {
                return callback()
            }
        },
        showMessage(e) {
            let obj = {};
            obj = this.callOption.find((item)=>{ //这里的callOption就是上面遍历的数据源
                return item.TypeId === e;     //筛选出匹配数据
            });
            this.callForm.typeName = obj.TypeName  // label
            this.callForm.typeId = e            // value
            console.log('changeOption', e, obj.TypeName)
        },
        // 发布寻味道
        submit() {
            console.log(this.callForm.endTime)
            this.$refs.callFormRef.validate((valid) => {
                if (!valid)
                    return this.$message({
                        showClose: true,
                        message: '输入数据无效',
                        type: 'warning',
                    })

                var config = {
                    method: 'post',
                    url: '/findG/add',
                    headers: { 
                        'Content-Type': 'application/json',
                        'Authorization': "Bearer "+ window.sessionStorage.getItem('token') 
                    },
                    data : this.callForm
                };
                var that = this
                this.$http(config)
                .then(function (response) {
                    console.log(Response, that.callForm.typeId, that.callForm.typeName);
                    if (response.status == 200) {
                        that.$router.push('/myconvene')
                        window.sessionStorage.setItem('activeNav', '/myconvene')
                        that.$store.commit('call/set_activeNav', '/myconvene')
                        that.$message({ showClose: true, message: response.message,type: 'success'})
                        that.uploadVisible = true
                    } else {
                        that.$message({showClose: true, message:response.message, type: 'error'})
                    }
                })
                .catch(function (error) {
                    console.log(error);
                    return that.$message({showClose: true, message:'请求错误', type: 'error'})
                });
            })
        },
        // 重置
        reset() {
            console.log('reset convene form')
            this.$refs.callFormRef.resetFields()
        },
    }
    
}
</script>

<style lang="less" scoped>
div>h2 {
  text-align: center;
}

</style>