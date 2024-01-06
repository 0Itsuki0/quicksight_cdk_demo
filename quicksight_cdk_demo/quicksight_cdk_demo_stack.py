from aws_cdk import (
    Stack,
    aws_quicksight, 
    RemovalPolicy, 
    aws_iam, 
    aws_s3, 
)

from constructs import Construct

class QuicksightCdkDemoStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.bucket_name = "bucket_name"
        self.username = "user_name"
        
        self.catalog="AwsDataCatalog",
        self.schema="database_name"
        self.table = "table_name"

        self.grant_S3_permission()
        self.create_quicksight_permissions()
        self.create_quicksight_datasource()
        self.create_quicksight_dataset()
        # self.create_refresh_schedule()
        self.create_analysis()
        self.create_template()
        self.create_dashboard()
        
        
    


    def grant_S3_permission(self):
        bucket = aws_s3.Bucket.from_bucket_name(
            scope=self, 
            id="quicksightCdkDemoBucket", 
            bucket_name=self.bucket_name
        )
        quicksight_s3_role = aws_iam.Role.from_role_name(
            scope=self, 
            id="quicksight_s3_role",
            role_name="service-role/aws-quicksight-s3-consumers-role-v0"
        )
        # quicksight_s3_role = aws_iam.Role.from_role_arn(
        #     scope=self, 
        #     id="quicksight_s3_role",
        #     role_arn=f"arn:aws:iam::{self.account}:role/service-role/aws-quicksight-s3-consumers-role-v0"
        # )
        bucket.grant_read_write(quicksight_s3_role)
        
        
                
    def create_quicksight_permissions(self):
        self.principal=f"arn:aws:quicksight:{self.region}:{self.account}:user/default/{self.username}"
        
        self.data_source_permissions = [
            aws_quicksight.CfnDataSource.ResourcePermissionProperty(
                principal=self.principal,
                actions=[
                    "quicksight:UpdateDataSourcePermissions", 
                    "quicksight:DescribeDataSourcePermissions", 
                    "quicksight:PassDataSource", 
                    "quicksight:DescribeDataSource", 
                    "quicksight:DeleteDataSource", 
                    "quicksight:UpdateDataSource",
                ],
            ),
        ]

        self.dataset_permissions = [
            aws_quicksight.CfnDataSet.ResourcePermissionProperty(
                principal=self.principal,
                actions=[
                    "quicksight:PassDataSet", 
                    "quicksight:DescribeIngestion", 
                    "quicksight:CreateIngestion", 
                    "quicksight:UpdateDataSet", 
                    "quicksight:DeleteDataSet", 
                    "quicksight:DescribeDataSet", 
                    "quicksight:CancelIngestion", 
                    "quicksight:DescribeDataSetPermissions", 
                    "quicksight:ListIngestions", 
                    "quicksight:UpdateDataSetPermissions"
                ],
            )
        ]
        
        self.analysis_permissions = [
            aws_quicksight.CfnAnalysis.ResourcePermissionProperty(
                principal=self.principal,
                actions=[
                    "quicksight:RestoreAnalysis",
                    "quicksight:UpdateAnalysisPermissions", 
                    "quicksight:DeleteAnalysis", 
                    "quicksight:QueryAnalysis", 
                    "quicksight:DescribeAnalysisPermissions", 
                    "quicksight:DescribeAnalysis", 
                    "quicksight:UpdateAnalysis"
                ],
            )
        ]
        
        self.template_permissions = [
            aws_quicksight.CfnTemplate.ResourcePermissionProperty(
                principal=self.principal,
                actions=[
                    "quicksight:UpdateTemplatePermissions", 
                    "quicksight:DescribeTemplatePermissions", 
                    "quicksight:UpdateTemplateAlias", 
                    "quicksight:DeleteTemplateAlias", 
                    "quicksight:DescribeTemplateAlias", 
                    "quicksight:ListTemplateAliases", 
                    "quicksight:ListTemplates", 
                    "quicksight:CreateTemplateAlias", 
                    "quicksight:DeleteTemplate", 
                    "quicksight:UpdateTemplate", 
                    "quicksight:ListTemplateVersions", 
                    "quicksight:DescribeTemplate", 
                    "quicksight:CreateTemplate"
                ],
            )
        ]
        
        self.dashboard_permissions = [
            aws_quicksight.CfnDashboard.ResourcePermissionProperty(
                principal=self.principal,
                actions=[
                    "quicksight:DescribeDashboard", 
                    "quicksight:ListDashboardVersions", 
                    "quicksight:UpdateDashboardPermissions", 
                    "quicksight:QueryDashboard", 
                    "quicksight:UpdateDashboard", 
                    "quicksight:DeleteDashboard", 
                    "quicksight:UpdateDashboardPublishedVersion", 
                    "quicksight:DescribeDashboardPermissions"
                ],
            )
        ]
        
    # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_quicksight/CfnDataSource.html
    def create_quicksight_datasource(self):
        self.quicksight_datasource = aws_quicksight.CfnDataSource(
            scope=self, 
            id="quickSightCdkDemoDatasource", 
            name="quickSightCdkDemoDatasource",
            data_source_id=f"quickSightCdkDemoDatasource",
            aws_account_id=self.account, 
            permissions=self.data_source_permissions, 
            data_source_parameters=aws_quicksight.CfnDataSource.DataSourceParametersProperty(
                athena_parameters=aws_quicksight.CfnDataSource.AthenaParametersProperty(
                    work_group="primary"
                )
            ), 
            type='ATHENA'
        )
        self.quicksight_datasource.apply_removal_policy(RemovalPolicy.DESTROY)

        
    # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_quicksight/CfnDataSet.html
    def create_quicksight_dataset(self):
        self.quicksight_dataset = aws_quicksight.CfnDataSet(
            scope=self, 
            id="quickSightCdkDemoDataSet", 
            name="quickSightCdkDemoDataSet",
            data_set_id="quickSightCdkDemoDataSet",
            aws_account_id=self.account, 
            physical_table_map={ 
                "quickSightAthenaDataSetPhysicalTableMap": aws_quicksight.CfnDataSet.PhysicalTableProperty(
                    custom_sql=aws_quicksight.CfnDataSet.CustomSqlProperty(
                        columns=[aws_quicksight.CfnDataSet.InputColumnProperty(
                            name="col_name",
                            type="STRING",
                        )],
                        data_source_arn=self.quicksight_datasource.attr_arn,
                        name="custom_sql",
                        sql_query=f"select * from {self.catalog}.{self.schema}.{self.table}", 
                    ),
                    # relational_table=aws_quicksight.CfnDataSet.RelationalTableProperty(
                    #     data_source_arn=self.quicksight_datasource.attr_arn,
                    #     input_columns=[
                    #         aws_quicksight.CfnDataSet.InputColumnProperty(
                    #             name="col_name",
                    #             type="STRING",
                    #         ),
                    #         aws_quicksight.CfnDataSet.InputColumnProperty(
                    #             name="createdate",
                    #             type="DATETIME",
                    #         )
                    #     ],
                    #     name=self.table,
                    #     catalog=self.catalog,
                    #     schema=self.schema
                    # )
                )
            },
            logical_table_map={
                "quickSightAthenaDataSetLogicalTableMap": aws_quicksight.CfnDataSet.LogicalTableProperty(
                    alias="user_master",
                    source=aws_quicksight.CfnDataSet.LogicalTableSourceProperty(
                        physical_table_id="quickSightAthenaDataSetPhysicalTableMap"
                    )
                )
            }, 
            permissions=self.dataset_permissions,
            import_mode="DIRECT_QUERY" # 'SPICE'|'DIRECT_QUERY',
        )
        self.quicksight_dataset.apply_removal_policy(RemovalPolicy.DESTROY)


    def create_refresh_schedule(self):
        self.refresh_schedule = aws_quicksight.CfnRefreshSchedule(
            scope=self, 
            id="DatasetRefreshSchedule",
            aws_account_id=self.account,
            data_set_id=self.quicksight_dataset.data_set_id,
            schedule=aws_quicksight.CfnRefreshSchedule.RefreshScheduleMapProperty(
                refresh_type="FULL_REFRESH", # 'INCREMENTAL_REFRESH'|'FULL_REFRESH',
                schedule_frequency=aws_quicksight.CfnRefreshSchedule.ScheduleFrequencyProperty(
                    interval="DAILY", # 'MINUTE15'|'MINUTE30'|'HOURLY'|'DAILY'|'WEEKLY'|'MONTHLY',
                    # refresh_on_day=aws_quicksight.CfnRefreshSchedule.RefreshOnDayProperty(
                    #     day_of_month="dayOfMonth",
                    #     day_of_week="dayOfWeek"
                    # ),
                    # time_of_the_day="timeOfTheDay",
                    # time_zone="timeZone"
                ),
                schedule_id="quicksightDatasetRefreshSchedule",
                # start_after_date_time="startAfterDateTime"
            )
        )
        
    def create_analysis(self):
        analysis_defaults_property = aws_quicksight.CfnAnalysis.AnalysisDefaultsProperty(
            default_new_sheet_configuration=aws_quicksight.CfnAnalysis.DefaultNewSheetConfigurationProperty(
                interactive_layout_configuration=aws_quicksight.CfnAnalysis.DefaultInteractiveLayoutConfigurationProperty(
                    # free_form=aws_quicksight.CfnAnalysis.DefaultFreeFormLayoutConfigurationProperty(
                    #     canvas_size_options=aws_quicksight.CfnAnalysis.FreeFormLayoutCanvasSizeOptionsProperty(
                    #         screen_canvas_size_options=aws_quicksight.CfnAnalysis.FreeFormLayoutScreenCanvasSizeOptionsProperty(
                    #             optimized_view_port_width="optimizedViewPortWidth"
                    #         )
                    #     )
                    # ),
                    # tiled
                    grid=aws_quicksight.CfnAnalysis.DefaultGridLayoutConfigurationProperty(
                        canvas_size_options=aws_quicksight.CfnAnalysis.GridLayoutCanvasSizeOptionsProperty(
                            screen_canvas_size_options=aws_quicksight.CfnAnalysis.GridLayoutScreenCanvasSizeOptionsProperty(
                                resize_option="FIXED", # FIXED | RESPONSIVE
                                # the properties below are optional
                                optimized_view_port_width="1600px"
                            )
                        )
                    )
                ),
                # paginated_layout_configuration=aws_quicksight.CfnAnalysis.DefaultPaginatedLayoutConfigurationProperty(
                #     section_based=aws_quicksight.CfnAnalysis.DefaultSectionBasedLayoutConfigurationProperty(
                #         canvas_size_options=aws_quicksight.CfnAnalysis.SectionBasedLayoutCanvasSizeOptionsProperty(
                #             paper_canvas_size_options=aws_quicksight.CfnAnalysis.SectionBasedLayoutPaperCanvasSizeOptionsProperty(
                #                 paper_margin=aws_quicksight.CfnAnalysis.SpacingProperty(
                #                     bottom="bottom",
                #                     left="left",
                #                     right="right",
                #                     top="top"
                #                 ),
                #                 paper_orientation="paperOrientation",
                #                 paper_size="paperSize"
                #             )
                #         )
                #     )
                # ),
                sheet_content_type="INTERACTIVE" # PAGINATED | INTERACTIVE
            )
        )

        sheet_definitions = [
            aws_quicksight.CfnAnalysis.SheetDefinitionProperty(
                sheet_id="firstDemoSheet", 
                content_type="INTERACTIVE", # PAGINATED | INTERACTIVE,
                name="firstDemoSheet", 
                # visuals=
            ),
            aws_quicksight.CfnAnalysis.SheetDefinitionProperty(
                sheet_id="SecondDemoSheet", 
                content_type="INTERACTIVE", # PAGINATED | INTERACTIVE,
                name="SecondDemoSheet", 
                # visuals=
            )
        ]
        
        dataset_identifiers = [aws_quicksight.CfnAnalysis.DataSetIdentifierDeclarationProperty(
            data_set_arn=self.quicksight_dataset.attr_arn, 
            identifier=self.quicksight_dataset.name
        )]
        
        self.quicksight_analysis = aws_quicksight.CfnAnalysis(
            scope=self, 
            id="QuickSightCdkDemoAnalysis",
            analysis_id="QuickSightCdkDemoAnalysis",
            name="QuickSightCdkDemoAnalysis",
            aws_account_id=self.account,
            definition=aws_quicksight.CfnAnalysis.AnalysisDefinitionProperty(
                data_set_identifier_declarations=dataset_identifiers,
                analysis_defaults=analysis_defaults_property, 
                sheets=sheet_definitions
            ), 
            permissions=self.analysis_permissions,             
        )
        self.quicksight_analysis.apply_removal_policy(RemovalPolicy.DESTROY)
        
        
        
    def create_template(self):
        self.template = aws_quicksight.CfnTemplate(
            scope=self, 
            id="quicksightCdkDemoTemplate", 
            aws_account_id=self.account,
            template_id="quicksightCdkDemoTemplate", 
            name="quicksightCdkDemoTemplate",
            permissions=self.template_permissions, 
            source_entity=aws_quicksight.CfnTemplate.TemplateSourceEntityProperty(
                source_analysis=aws_quicksight.CfnTemplate.TemplateSourceAnalysisProperty(
                    arn=self.quicksight_analysis.attr_arn,
                    data_set_references=[aws_quicksight.CfnTemplate.DataSetReferenceProperty(
                        data_set_arn=self.quicksight_dataset.attr_arn,
                        data_set_placeholder="quicksightDemoDataset"
                    )]
                ),
            )
        )
        self.template.apply_removal_policy(RemovalPolicy.DESTROY)
    
    
    def create_dashboard(self):
        self.dashboard = aws_quicksight.CfnDashboard(
            scope=self, 
            id="quicksightCdkDemoDashbaord", 
            aws_account_id=self.account, 
            dashboard_id="quicksightCdkDemoDashbaord", 
            name="quicksightCdkDemoDashbaord", 
            permissions=self.dashboard_permissions, 
            source_entity=aws_quicksight.CfnDashboard.DashboardSourceEntityProperty(
                source_template=aws_quicksight.CfnDashboard.DashboardSourceTemplateProperty(
                    arn=self.template.attr_arn,
                    data_set_references=[aws_quicksight.CfnDashboard.DataSetReferenceProperty(
                        data_set_arn=self.quicksight_dataset.attr_arn,
                        data_set_placeholder="quicksightDemoDataset"
                    )]
                )
            )
        )
        self.dashboard.apply_removal_policy(RemovalPolicy.DESTROY)
