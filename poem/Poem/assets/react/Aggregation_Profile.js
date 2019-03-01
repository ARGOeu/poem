import React, { Component } from 'react';
import { Formik, Field, FieldArray, Form, connect } from 'formik';
import FormikEffect from './FormikEffect.js'

const MetricProfileAPI = 'https://web-api-devel.argo.grnet.gr/api/v2/metric_profiles'
const AggregationProfileAPI = 'https://web-api-devel.argo.grnet.gr/api/v2/aggregation_profiles/'
const TokenAPI = 'https://<tenant-host>/poem/api/v2/internal/tokens'


class App extends Component {
    constructor(props) {
        super(props)

        this.profile_id = props.django.apiid
        this.django_view = props.django.view
        this.tenant_host = TokenAPI.replace('<tenant-host>', props.django.tenant_host)

        this.state = {
        loading: false,
        aggregation_profile: {},
        metric_profile: {},
        list_metric_profiles: {},
        }
        this.fetchMetricProfiles = this.fetchMetricProfiles.bind(this)
        this.fetchAggregationProfile = this.fetchAggregationProfile.bind(this)
        this.extractListOfMetricsProfiles = this.extractListOfMetricsProfiles.bind(this)
        this.onMetricProfileChange = this.onMetricProfileChange.bind(this)

        this.logic_operations = ["OR", "AND"] 
        this.endpoint_groups = ["servicegroups", "sites"]
    }
    fetchToken() {
        return fetch(this.tenant_host)
            .then(response => response.json())
            .then(array => array[0]['token'])
            .catch(err => console.log('Something went wrong: ' + err))
    }

    fetchMetricProfiles(token) {
        return fetch(MetricProfileAPI, 
            {headers: {"Accept": "application/json",
                "x-api-key": token}})
            .then(response => response.json())
            .then(json => json['data']) 
            .catch(err => console.log('Something went wrong: ' + err))
    }

    fetchAggregationProfile(token, idProfile) {
        return fetch(AggregationProfileAPI + idProfile, 
            {headers: {"Accept": "application/json",
                 "x-api-key": token}})
            .then(response => response.json())
            .then(json => json['data'])
            .then(array => array[0])
            .catch(err => console.log('Something went wrong: ' + err))
    }

    onMetricProfileChange(event) {
        let selected_profile = {name: event.target.value}
        let list_services = this.extractListOfServices(selected_profile,
            this.state.list_metric_profiles)
        this.setState({list_services: list_services})
    }

    extractListOfMetricsProfiles(allProfiles) {
        var list_profiles = []

        allProfiles.forEach(profile => {
            var i = list_profiles['length']
            var {name, id} = profile

            list_profiles[i] = {name, id}
            i += 1
        })

        return list_profiles
    }


    extractListOfServices(profileFromAggregation, listMetricProfiles)
    {
        let targetProfile = listMetricProfiles.filter(p => p.name === profileFromAggregation.name)

        return targetProfile[0].services.map(s => s.service)
    }

    insertSelectPlaceholder(data, text) {
        if (data) {
            return [text, ...data]
        } else {
            return [text] 
        }
    }

    componentWillMount() {
        this.setState({loading: true})

        if (this.django_view === 'change') {
            this.fetchToken().then(token => 
                Promise.all([this.fetchAggregationProfile(token, this.profile_id), this.fetchMetricProfiles(token)])
                .then(([aggregp, metricp]) => this.setState(
            {
                aggregation_profile: aggregp, 
                list_metric_profiles: metricp,
                list_services: this.extractListOfServices(aggregp.metric_profile, metricp),
                loading: false
            }))
            )
        }
        else if (this.django_view === 'add') {
            let empty_aggregation_profile = {
                name: '',
                metric_operation: '',
                profile_operation: '',
                endpoint_group: '',
                metric_profile: {
                    name: ''
                },
                groups: []
          }
            this.fetchToken().then(token => this.fetchMetricProfiles(token))
                .then(metricp => this.setState(
            {
                aggregation_profile: empty_aggregation_profile,
                list_metric_profiles: metricp,
                list_services: [],
                loading: false
            }))
        }
    }

    render() {
        const {aggregation_profile, list_metric_profiles, list_services, loading} = this.state

    return (
        <div className="App">
            { 
                (loading) ? 
                    <div>Loading profiles...</div> : 
                    (!aggregation_profile && !list_metric_profiles) ?
                    <div>No profile loaded</div> :
                    <Formik
                        initialValues={{
                            name: aggregation_profile.name, 
                            metric_operation: aggregation_profile.metric_operation,
                            profile_operation: aggregation_profile.profile_operation,
                            metric_profile: aggregation_profile.metric_profile.name,
                            endpoint_group: aggregation_profile.endpoint_group,
                            groups: aggregation_profile.groups
                        }}  
                        onSubmit = {(values, actions) => alert(JSON.stringify(values, null, 2))}
                        render = {props => (
                            <Form>
                            <section>
                            <FormikEffect onChange={(current, prev) => {
                                if (current.values.metric_profile !== prev.values.metric_profile) {
                                    let selected_profile = {name: current.values.metric_profile}
                                    this.setState({list_services:
                                        this.extractListOfServices(selected_profile,
                                        list_metric_profiles)})
                                }
                            }}
                            />
                            <p>
                                <label>Aggregation profile: </label>
                                <Field type="text" name="name" placeholder="Name of aggregation profile"/>
                            </p>
                            <p>
                                <label>Metric operation: </label>
                                <Field 
                                    name="metric_operation" 
                                    component={DropDown} 
                                    data={this.insertSelectPlaceholder(this.logic_operations, '<Operation>')}/> 
                            </p>
                            <p>
                                <label>Profile operation: </label>
                                <Field 
                                    name="profile_operation" 
                                    component={DropDown} 
                                    data={this.insertSelectPlaceholder(this.logic_operations, '<Operation>')}/> 
                            </p>
                            <p>
                                <label>Metric profile: </label>
                                <Field 
                                    name="metric_profile" 
                                    component={DropDown} 
                                    data={this.insertSelectPlaceholder(list_metric_profiles.map(e => e.name), '<Metric profile>')}
                                />
                            </p>
                            <p>
                                <label>Endpoint group: </label>
                                <Field 
                                    name="endpoint_group" 
                                    component={DropDown} 
                                    data={this.insertSelectPlaceholder(this.endpoint_groups, '<Endpoint group>')}/> 
                            </p>
                            <FieldArray
                                name="groups"
                                render={props => (
                                    <GroupList
                                        {...props}
                                        list_services={this.insertSelectPlaceholder(list_services, '<Service flavour>')}
                                        list_operations={this.insertSelectPlaceholder(this.logic_operations, '<Operation>')}
                                    />)}
                            />
                            </section>
                            <button type="submit">Save</button>
                            </Form>
                        )}
                    />
            }
        </div>
    );}
}


const DropDown = ({field, data=[], prefix=""}) => 
    <Field component="select"
        name={prefix ? `${prefix}.${field.name}` : field.name}
        required={true}>
        {
            data.map((name, i) => 
                i === 0 ?
                <option key={i} hidden>{name}</option> :
                <option key={i} value={name}>{name}</option>
            )
        }
    </Field>

const ButtonAdd = ({label, obj={}, operation=f=>f}) => 
    <button
        type="button"
        onClick={() => operation(obj)}>
        {label}
    </button>

const ButtonRemove = ({label, index=0, operation=f=>f}) => 
    <button
        type="button"
        onClick={() => operation(index)}>
        {label}
    </button>

const GroupList = ({name, form, list_services, list_operations, push}) =>
    <div className="groups">
        { (form.values.groups.length === 0) ?
                <div className="group-add">
                    <p>No Groups listed. (Add a group)</p> 
                    <ButtonAdd 
                        label="Add new group"
                        obj={{name: '', operation: '',
                              services: [{name: '', operation: ''}]}}
                        operation={push}/>
                </div> :
                form.values[name].map((group, i) =>
                    <FieldArray
                        key={i}
                        name="groups"
                        render={props => (
                            <Group
                                {...props}
                                key={i}
                                operation={group.operation}
                                services={group.services}
                                list_services={list_services}
                                list_operations={list_operations}
                                groupindex={i}
                                last={i === form.values[name].length - 1}
                            />
                        )}
                    />
                )
        }
    </div>

const Group = ({name, operation, services, list_operations, list_services, form, groupindex, remove, push, last}) =>
    <div className="group" key={groupindex}>
        <fieldset className="groups-fieldset">
            <legend>
                <Field
                    name={`groups.${groupindex}.name`}
                    placeholder="Name of service group">
                </Field>
                <ButtonRemove
                    label="X"
                    index={groupindex}
                    operation={remove}/>
            </legend>
            <FieldArray
                name={`groups.${groupindex}`}
                render={props => (
                    <ServiceList
                        list_services={list_services}
                        list_operations={list_operations}
                        services={services}
                        groupindex={groupindex}
                        groupoperation={operation}
                        form={form}
                    />)}
            />
            { 
                (last) ?
                <div className="group-add">
                    <ButtonAdd 
                        label="Add new group"
                        obj={{name: '', operation: '',
                              services: [{name: '', operation: ''}]}}
                        operation={push}/>
                </div> :
                    null 
            }
        </fieldset>
        <div className="group-operation" key={groupindex}>
            {form.values.profile_operation}
        </div>
    </div>

const ServiceList = ({services, list_services=[], list_operations=[], groupindex, groupoperation, push}) =>
    <fieldset className="services-fieldset">
        <legend align="center">
            <DropDown 
                field={{name: "operation", value: groupoperation}}
                data={list_operations}
                prefix={`groups.${groupindex}`}
            />
        </legend>
        { 
            (services.length === 0) ?
                <div className="services-add">
                    <p>No Services listed. (Add a service)</p>
                    <ButtonAdd 
                        label="Add new service"
                        obj={{name: '', operation: ''}}
                        operation={push}/>
                </div> :
                services.map((service, i) =>
                    <FieldArray
                        key={i}
                        name={`groups.${groupindex}.services`}
                        render={props => (
                            <Service
                                {...props}
                                key={i}
                                operation={service.operation} 
                                list_services={list_services} 
                                list_operations={list_operations} 
                                groupindex={groupindex}
                                index={i}
                                last={i === services.length - 1}
                            />
                        )}
                    />
            )
        }
    </fieldset>

const Service = ({name, operation, list_services, list_operations, groupindex, index, remove, push, last}) => 
    <div className="service" key={index}>
        <DropDown 
            field={{name: "name", value: name}}
            data={list_services} 
            prefix={`groups.${groupindex}.services.${index}`}
        />
        <DropDown 
            field={{name: "operation", value: operation}}
            data={list_operations}
            prefix={`groups.${groupindex}.services.${index}`}
        />
        <ButtonRemove
            label="-"
            index={index}
            operation={remove}/>
        { (last) ?
            <div className="services-add">
                <ButtonAdd
                    label="+"
                    obj={{name: '', operation: ''}}
                    operation={push}/>
            </div> :
                null
        }
    </div>


export default App;
