<template>
    <div style="height: 100%">
        <!-- 面包屑 -->
        <el-breadcrumb separator-class="el-icon-arrow-right" style="margin-bottom: 10px">
            <el-breadcrumb-item :to="{ path: '/welcome' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>分享美食</el-breadcrumb-item>
            <el-breadcrumb-item>已经发起的寻味道请求信息</el-breadcrumb-item>
        </el-breadcrumb>
        <!-- 信息主体 -->
        <h2>分享列表信息</h2>
        <el-card>
            <el-table :data="tableData" :header-cell-style="{'text-align':'center'}" 
                      :cell-style="{'text-align':'center'}" border>
                <el-table-column prop="id" label="请求标识" width="100"></el-table-column>
                <el-table-column prop="findGId" label="请求寻味道标识" width="150"></el-table-column>
                <el-table-column prop="findGName" label="寻味道名字" width="150"></el-table-column>
                <el-table-column prop="userId" label="请求者ID" width="100"></el-table-column>
                <el-table-column prop="description" label="请求描述" ></el-table-column>
                <el-table-column prop="createTime" label="创建请求时间" width="180"></el-table-column>
                <el-table-column prop="modifyTime" label="修改请求时间" width="180"></el-table-column>
                <el-table-column prop="state" label="状态" width="100"></el-table-column>
                <el-table-column label="操作" width="220">
                    <template slot-scope='scope'>
                        <el-tooltip effect="dark" :enterable="false" content="修改此条请求" placement="top">
                            <el-button type="primary" :disabled="scope.row.state == '同意' || scope.row.state == '拒绝'" icon="el-icon-edit" @click="addEditVisable(scope.row.id, scope.row.findGId, scope.row.userId, scope.row.description)"></el-button>
                        </el-tooltip>
                        <el-tooltip effect="dark" :enterable="false" content="删除此条请求" placement="top">
                           <el-button type="danger" :disabled="scope.row.state == '同意' || scope.row.state == '拒绝'" icon="el-icon-delete" @click="addDeleteVisable(scope.row.id)"></el-button>
                        </el-tooltip>
                        <el-tooltip effect="dark" :enterable="false" content="查看寻味道信息" placement="top">
                            <el-button type="primary" :disabled="scope.row.state != '同意'" icon="el-icon-chat-dot-square" @click="checkCall(scope.row.findGId)"></el-button>
                        </el-tooltip>
                    </template>
                </el-table-column>
            </el-table>
            <div class="card_foot">
                <div class="block" style="margin: 5px 0px; float: left;">
                    <el-pagination
                    @size-change="handleSizeChange"
                    @current-change="handleCurrentChange"
                    :current-page="page"
                    :page-sizes="[2, 5, 10, 15]"
                    :page-size="rows"
                    layout="total, sizes, prev, pager, next, jumper"
                    :total="total">
                    </el-pagination>
                </div>
            </div>
        </el-card>

        <!-- 修改请求信息 -->
        <el-dialog title="修改请求信息" :visible.sync="editVisable" width="50%">
            <el-form label-width="120px" style="margin:10px 20px 10px 10px" >
                <el-form-item label="请求标识">
                    <el-input v-model="request.id" disabled></el-input>
                </el-form-item>
                <el-form-item label="寻味道ID">
                    <el-input v-model="request.findGId" disabled></el-input>
                </el-form-item>
                <el-form-item label="请求者ID">
                    <el-input v-model="request.userId" disabled></el-input>
                </el-form-item>
                <el-form-item label="请求描述">
                    <el-input type="textarea" v-model="request.description" required></el-input>
                </el-form-item>
            </el-form>
            <span slot="footer" class="dialog-footer">
                <el-button @click="notEdit()">取 消</el-button>
                <el-button type="primary" @click="Edit()">确 定</el-button>
            </span>
        </el-dialog>

        <!-- 自己所有已经接令的寻味道信息 -->
        <el-dialog title="寻味道详情" :visible.sync="infoVisable" width="50%">
            <div>
                <span style="font-size: 20px; margin-right: 10px;">寻味道图片</span>
                <el-button type="primary" @click="checkPic()" size="mini" style="margin-bottom: 5px;" icon="el-icon-picture"></el-button>
            </div>
            
            <table style="width: 100%" class="myTable">
                <tr v-for="item in call">
                    <td class="column">{{ item[0] }}</td>
                    <td class="column">{{ item[1] }}</td>
                </tr>
            </table>
        </el-dialog>

        <!-- 展示图片 -->
        <el-dialog title="寻味道相关图片" :visible.sync="picVisable">
            <el-image v-show="havePic" v-for="url in srcList" :key="url" :src="url" lazy></el-image>
            <span v-show="!havePic">暂无照片</span>
        </el-dialog>
    </div>
</template>

<script>
export default {
    data() {
        return {
            havePic: true,
            picVisable: false,
            srcInitUrl: '',
            srcList: [],

            tableData: [],          // el-table数据
            page: 1,                // 数据页数
            rows: 10,                // 每页行数
            total: 0,               // 数据总数
            editVisable: false,     // 请求表单是否可见
            infoVisable: false,     // 查看寻味道信息是否可见
            call: [],
            request: {
                id: '',
                userId: '',
                findGId: '',
                findGName: '',
                description: ''
            }
        }
    },
    created() {
        this.init()
    },
    methods: {
        checkPic() {
            var that = this
            that.havePic = true
            this.$http.get('/findG/getGraphByFindGId/'+this.call[0][1], {
                headers: {
                    'Authorization': "Bearer "+ window.sessionStorage.getItem('token') 
                }
            }).then(function(response) {
                if(response.status != 200) {
                    return that.$message({showClose: true, message: response.message, type: 'warning'})
                }
                var data = response.data
                if (data.length == 0) {
                    that.havePic = false
                    that.picVisable = true
                    return
                }
                that.srcList = []
                for(var i = 0; i < data.length; ++ i) {
                    that.srcList.push('http://localhost:8000/static/UserImages/' + data[i]['graphLocation']) +'.jpg'
                }
                that.srcInitUrl = that.srcList[0]
                that.picVisable = true
            }).catch(function(error) {
                console.log(error, '/findG/getGraphByFindGId/'+this.call.id)
                return that.$message({showClose: true, message: "请求错误", type: 'error'})
            })
        },
        init() {
            var that = this
            this.$http.get('/pleEat/pageFind/byUser/'+ this.page+'/'+ this.rows+'/'+this.$store.state.user.id, {
                                headers: {
                                    'Authorization': "Bearer "+ window.sessionStorage.getItem('token')
                                }
                            })
            .then(function(response) {
                console.log('acceptList');
                for(var i = 0; i < response.data.records.length; i ++) {
                    switch (response.data.records[i]['state']) {
                        case 0:
                            response.data.records[i]['state'] = "待处理";
                            break;
                        case 1:
                            response.data.records[i]['state'] = "同意";
                            break;
                        case 2:
                            response.data.records[i]['state'] = "拒绝";
                            break;
                        case 3:
                            response.data.records[i]['state'] = "取消";
                            break;
                        case 4:
                            response.data.records[i]['state'] = "响应中";
                            break;
                        default:
                            break;
                    }
                }
                that.tableData = response.data.records
                that.total = response.data.total
            })
            .catch(function(error) {
                console.log(error)
                return that.$message({showClose: true, message:'请求错误', type: 'error'})
            })
        },
        // 点击修改请求按钮显示对话框组件
        addEditVisable(id, findGId, userId, des) {
            this.editVisable = true
            this.request.id = id
            this.request.findGId = findGId
            this.request.userId = userId
            this.request.description = des
        },
        // 点击取消请求或者点击空白处提示信息
        notEdit() {
            this.editVisable = false
            this.$message({showClose: true, message: '取消修改请求'})
        },
        // 点击 确定修改请求按钮
        Edit() {
            this.editVisable = false
            var data = JSON.stringify(this.request);
            var that = this
            var config = {
                method: 'post',
                url: '/pleEat/modify',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': "Bearer "+ window.sessionStorage.getItem('token')
                },
                data : data
            };
            this.$http(config)
            .then(function (response) {
                if (response.status == 200) {
                    that.$message({showClose: true, message: response.message, type: 'success'})
                    that.init()
                } else {
                    that.$message({showClose: true, message: response.message, type: 'warning'})
                }
            })
            .catch(function (error) {
                console.error();
                return that.$message({showClose: true, message:'请求错误', type: 'error'})
            });
        },
        // 点击 删除请求按钮 展示消息组件
        addDeleteVisable(id) {
            var that = this
            this.$confirm('是否删除此请求?', '警告', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning',
                center: true
            })
            .then(() => {
                console.log(id, 'makesure delete')
                var config = {
                    method: 'post',
                    url: '/pleEat/deleteById/'+id,
                    headers: { 
                        'Content-Type': 'application/json',
                        'Authorization': "Bearer "+ window.sessionStorage.getItem('token')
                    },
                };
                this.$http(config)
                .then(function (response) {
                    if (response.status == 200) {
                        that.$message({ showClose: true, message: response.message, type: 'success' })
                        that.init()
                    } else {
                        that.$message({ showClose: true, message: response.message, type: 'warning' })
                    }
                })
                .catch(function (response) {
                    that.$message({ showClose: true, message: response.message, type: 'error' })
                })
            })
            .catch(() => {
                this.$message({ showClose: true,  message: '已取消删除', type: 'info' });
            });
        },
        // 点击显示详细信息按钮展示信息
        checkCall(id) {
            var that = this
            this.$http.get(`/findG/findById/${id}`,{
                                headers: {
                                    'Authorization': "Bearer "+ window.sessionStorage.getItem('token')
                                }
                            })
            .then(function(response) {
                that.call = new Array(11)
                if (response.status == 200) {
                    Object.getOwnPropertyNames(response.data).forEach(function(key){
                        switch(key) {
                            case 'id': that.call[0] =['寻味道标识', response.data[key]]; break;
                            case 'userId': that.call[1] = ['发布者ID', response.data[key]]; break;
                            case 'typeName': that.call[2] = ['寻味道类型', response.data[key]]; break;
                            case 'name': that.call[3] = ['寻味道名称', response.data[key]]; break;
                            case 'description': that.call[4] = ['寻味道描述', response.data[key]]; break;
                            case 'people': that.call[5] = ['已寻找人数', response.data[key]]; break;
                            case 'peopleCount': that.call[6] = ['寻味道总人数', response.data[key]]; break;
                            case 'endTime': that.call[7] = ['寻找结束时间', response.data[key]]; break;
                            case 'createTime': that.call[8] = ['寻味道创建时间', response.data[key]]; break;
                            case 'modifyTime': that.call[9] = ['寻味道修改时间', response.data[key]]; break;
                            case 'stateName': that.call[10] = ['寻味道状态', response.data[key]]; break;
                            default: break;
                        }
                    })
                    that.infoVisable = true
                } else {
                    that.$message({showClose: true, message:'没有权限', type: 'error'})
                }
            })
            .catch(function(error) {
                console.error();
                return that.$message({showClose: true, message:'请求错误', type: 'error'})
            })
        },
        // 监听最新的pageSize
        handleSizeChange(newSize) {
            console.log(`每页 ${newSize} 条`)
            this.rows = newSize
            this.init()
        },
        // 监听页码值的改变
        handleCurrentChange(newPage) {
            console.log(`当前页: ${newPage}`)
            this.page = newPage
            this.init()
        },
    }
}
</script>

<style lang="less" scoped>
div {
    h2 {
        text-align: center;
    }
    .el-table {
        width: 100%;
        margin: 10px 0px
    }
}
</style>